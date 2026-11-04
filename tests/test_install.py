"""Exercise the real questionnaire and installed helpers in private temporary paths."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest

PACKAGE=Path(__file__).resolve().parents[1]


class InstallationFlowTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='skill install test ')
        self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)
        self.config=self.root/'private answers/config.json'
        self.state=self.root/'installed releases'
        self.codex=self.root/'codex skills'
        self.claude=self.root/'claude skills'
        self.context=self.root/'private context'
        self.args=[sys.executable,str(PACKAGE/'install.py'),'--client','both',
                   '--config',str(self.config),'--state-dir',str(self.state),
                   '--codex-dir',str(self.codex),'--claude-dir',str(self.claude)]
        self.basic=['','Example Person','en','Etc/UTC',str(self.context),'']

    def run_install(self, answers=None, extra=()):
        return subprocess.run([*self.args,*extra],input='\n'.join(answers or self.basic)+'\n',
                              text=True,capture_output=True)

    def profile(self):return json.loads(self.config.read_text())

    def helper(self, command, *args):
        return subprocess.run([sys.executable,str(self.codex/'skill-config/scripts/config.py'),command,*args],
                              env={**os.environ,'SKILLS_CONFIG':str(self.config)},text=True,capture_output=True)

    def test_questions_install_both_clients_and_helpers_use_private_answers(self):
        result=self.run_install()
        self.assertEqual(result.returncode,0,result.stderr)
        profile=self.profile()
        self.assertEqual(profile['user']['display_name'],'Example Person')
        self.assertEqual(profile['user']['language'],'en')
        self.assertEqual(self.config.stat().st_mode & 0o777,0o600)
        self.assertEqual(self.helper('get','user.timezone').stdout.strip(),'Etc/UTC')
        self.assertTrue((self.codex/'marketing-run/SKILL.md').is_file())
        self.assertTrue((self.claude/'review-run/SKILL.md').is_file())
        self.assertEqual(profile['installation']['commands']['review:code'],'review-code')
        # Installed resources resolve after following the symlink to the private release copy.
        self.assertTrue((self.codex/'marketing-run').resolve().parent.parent.joinpath('plugins/marketing/protocol/contract.md').is_file())
        self.assertNotIn(str(PACKAGE),profile['paths']['skills'])
        self.assertFalse((Path(profile['paths']['skills']).parent/'.git').exists())
        proc=subprocess.run([sys.executable,str(Path(profile['paths']['scripts'])/'tasks.py'),'add',
                             '--title','Fictional installation task','--type','Investigate'],
                            env={**os.environ,'SKILLS_CONFIG':str(self.config)},text=True,capture_output=True)
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertTrue((self.context/'vault/tasks/fictional-installation-task.md').is_file())
        self.assertNotIn(str(self.context),(PACKAGE/'manifest.json').read_text())

    def test_reinstallation_keeps_answers_and_existing_private_notes(self):
        self.assertEqual(self.run_install().returncode,0)
        note=self.context/'vault/index.md';note.parent.mkdir(parents=True,exist_ok=True);note.write_text('Private note')
        result=self.run_install(['','','','','',''])
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(self.profile()['user']['display_name'],'Example Person')
        self.assertEqual(note.read_text(),'Private note')
        self.assertEqual(self.run_install(['','Another Example','','','','']).returncode,0)
        self.assertEqual(self.profile()['user']['display_name'],'Another Example')

    def test_work_questions_and_new_repository_reach_runtime_consumer(self):
        answers=['work',*self.basic[1:],'example/project','example-person','OPS',
                 '{"casey example":"Lead"}','["Lead"]','[]']
        result=self.run_install(answers)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(self.profile()['work']['github_repository'],'example/project')
        self.assertEqual(self.profile()['work']['requester_aliases'],{'casey example':'Lead'})
        self.assertEqual(self.helper('get','work.issue_prefix').stdout.strip(),'OPS')

    def test_existing_skill_conflict_does_not_write_config_or_replace_skill(self):
        destination=self.codex/'skill-config';destination.mkdir(parents=True)
        (destination/'personal.txt').write_text('keep')
        result=self.run_install()
        self.assertNotEqual(result.returncode,0)
        self.assertEqual((destination/'personal.txt').read_text(),'keep')
        self.assertFalse(self.config.exists())
        self.assertFalse(self.claude.exists())

    def test_invalid_timezone_and_private_path_inside_package_are_rejected(self):
        for timezone,context in [('Not/AZone',str(self.context)),('Etc/UTC',str(PACKAGE/'private-data'))]:
            result=self.run_install(['','Example Person','en',timezone,context,''])
            self.assertNotEqual(result.returncode,0)
            self.assertFalse(self.config.exists())

    def test_answers_file_uses_same_schema_and_rejects_unknown_or_secret_fields(self):
        path=self.root/'answers.json'
        basic={'user.display_name':'Fixture','user.language':'en','user.timezone':'Etc/UTC','paths.brain':str(self.context)}
        path.write_text(json.dumps({**basic,'api_key':'not-a-secret-but-invalid'}))
        self.assertNotEqual(self.run_install(extra=['--answers',str(path)]).returncode,0)
        self.assertFalse(self.config.exists())
        path.write_text(json.dumps(basic))
        result=self.run_install(extra=['--answers',str(path)])
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(self.profile()['user']['display_name'],'Fixture')

    def test_empty_optional_fields_do_not_copy_authors_services_or_model_policy(self):
        self.assertEqual(self.run_install().returncode,0)
        profile=self.profile()
        self.assertEqual(profile['contexts'],{})
        self.assertEqual(profile['integrations'],{})
        self.assertEqual(profile['execution']['model_policy'],'')
        self.assertEqual(profile['work']['github_repository'],'')
        proc=subprocess.run([sys.executable,str(self.codex/'priorities/scripts/collect_github_prs.py')],
                            env={**os.environ,'SKILLS_CONFIG':str(self.config)},text=True,capture_output=True)
        self.assertEqual(proc.returncode,2)
        self.assertIn('Configure work.github_repository',proc.stderr)

    def test_private_locations_cannot_follow_future_skill_links(self):
        for which in ('config', 'context'):
            with self.subTest(which=which):
                if which == 'config':
                    args=self.args.copy()
                    args[args.index('--config')+1]=str(self.codex/'skill-config/private-profile.json')
                    result=subprocess.run(args,input='\n'.join(self.basic)+'\n',text=True,capture_output=True)
                else:
                    result=self.run_install(['','Example Person','en','Etc/UTC',str(self.codex/'skill-config/private-context'),''])
                self.assertNotEqual(result.returncode,0)
                self.assertFalse(self.config.exists())
                self.assertFalse(self.codex.exists())
                self.assertFalse(self.state.exists())

    def test_relative_existing_paths_use_profile_directory_and_copied_installer_can_repeat(self):
        self.assertEqual(self.run_install().returncode,0)
        profile=self.profile()
        profile['paths']['vault']='relative-vault'
        profile['paths']['tasks']='relative-tasks'
        self.config.write_text(json.dumps(profile))
        result=self.run_install(['','','','','',''])
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue((self.config.parent/'relative-vault/index.md').is_file())
        self.assertTrue((self.config.parent/'relative-tasks/index.md').is_file())
        copied=Path(self.profile()['paths']['skills']).parent/'install.py'
        args=self.args.copy();args[1]=str(copied)
        result=subprocess.run(args,input='\n'*6,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_damaged_installed_release_is_reported_and_preserved(self):
        self.assertEqual(self.run_install().returncode,0)
        before=self.config.read_bytes()
        helper=Path(self.profile()['paths']['skills'])/'skill-config/scripts/config.py'
        helper.write_text('raise SystemExit(73)\n')
        result=self.run_install(['','','','','',''])
        self.assertNotEqual(result.returncode,0)
        self.assertIn('damaged or changed',result.stderr)
        self.assertEqual(helper.read_text(),'raise SystemExit(73)\n')
        self.assertEqual(self.config.read_bytes(),before)

    def test_profile_cannot_replace_installation_state(self):
        args=self.args.copy();args[args.index('--config')+1]=str(self.state/'install-state.json')
        result=subprocess.run(args,input='\n'.join(self.basic)+'\n',text=True,capture_output=True)
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(self.state.exists())


if __name__=='__main__':unittest.main()
