import tempfile
import unittest
from pathlib import Path
from core import Ledger, ActivityClock, filename_group


class TrackingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Ledger(Path(self.tmp.name) / 'time.sqlite3')
        self.path = str(Path(self.tmp.name) / 'Body.spp')
        self.binding = self.db.bind(self.path, 'Wedding', 'Body')
        self.clock = ActivityClock(self.db)
        self.clock.switch(self.path)

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def total(self):
        return sum(row['total'] for row in self.db.summary(self.binding['work']))

    def test_idle_tail_is_not_counted(self):
        for mono in [0, 30, 50, 200, 210]:
            self.clock.input(mono, 1000+mono)
        self.clock.stop()
        self.assertEqual(self.total(), 60)

    def test_save_as_split_never_duplicates(self):
        self.clock.input(0, 1000)
        self.clock.input(60, 1060)
        hair = str(Path(self.tmp.name) / 'Hair.spp')
        self.db.auto_bind(hair)
        self.clock.switch(hair)
        self.clock.input(70, 1070)
        self.clock.input(90, 1090)
        self.clock.stop()
        self.db.bind(hair, 'Wedding', 'Hair', self.binding['work'])
        rows = {r['name']: r['total'] for r in self.db.summary(self.binding['work'])}
        self.assertEqual(rows, {'Body': 60, 'Hair': 20})

    def test_pause_does_not_bridge_gap(self):
        self.clock.input(0, 1000)
        self.clock.input(10, 1010)
        self.clock.stop()
        self.clock.input(20, 1020)
        self.clock.input(30, 1030)
        self.clock.stop()
        self.assertEqual(self.total(), 20)

    def test_checkpoints_are_idempotent(self):
        self.clock.input(0, 1000)
        self.clock.input(10, 1010)
        self.clock.flush()
        self.clock.input(20, 1020)
        self.clock.flush()
        self.clock.flush()
        self.assertEqual(self.total(), 20)

    def test_midnight_is_split(self):
        self.clock.input(0, 1000)
        self.clock.input(100, 1100)
        self.clock.flush()
        self.assertEqual(self.db.summary(self.binding['work'], 1050)[0]['today'], 50)

    def test_existing_destination_keeps_its_assignment(self):
        target = str(Path(self.tmp.name) / 'Other.spp')
        other = self.db.bind(target, 'Other', 'Head')
        self.assertEqual(self.db.auto_bind(target)['work'], other['work'])

    def test_filename_rules(self):
        for name, expected in [
            ('Penglai_Wedding.Basecolors.spp', ('Penglai_Wedding', 'Basecolors')),
            ('Penglai_Wedding.Hair_v02.spp', ('Penglai_Wedding', 'Hair')),
            ('Penglai_Wedding.spp', ('Penglai_Wedding', 'Main')),
            ('Robot_02.Arm2.spp', ('Robot_02', 'Arm2')),
        ]:
            self.assertEqual(filename_group(name), expected)

    def test_automatic_grouping_and_versions(self):
        base = self.db.auto_bind(str(Path(self.tmp.name) / 'Penglai_Wedding.Basecolors.spp'))
        hair = self.db.auto_bind(str(Path(self.tmp.name) / 'Penglai_Wedding.Hair.spp'))
        version = self.db.auto_bind(str(Path(self.tmp.name) / 'Penglai_Wedding.Hair_v02.spp'))
        self.assertEqual(base['work_name'], 'Penglai_Wedding')
        self.assertEqual(base['work'], hair['work'])
        self.assertNotEqual(base['part'], hair['part'])
        self.assertEqual(hair['part'], version['part'])
        self.assertEqual(self.db.auto_bind(version['path'])['part'], hair['part'])

    def test_manual_binding_survives_auto_discovery(self):
        self.assertEqual(self.db.auto_bind(self.path)['work'], self.binding['work'])

    def test_reopen_recovers_checkpoint(self):
        self.clock.input(0, 1000)
        self.clock.input(10, 1010)
        self.clock.flush()
        another = Ledger(Path(self.tmp.name) / 'time.sqlite3')
        self.assertEqual(another.summary(self.binding['work'])[0]['total'], 10)
        another.close()


if __name__ == '__main__':
    unittest.main()
