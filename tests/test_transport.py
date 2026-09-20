import unittest
from dongle_go.transport import ATTransport, TransportError


class SerialFixture:
    def __init__(self, chunks):
        self.chunks = iter(chunks)
        self.writes = []
        self.closed = False
    def reset_input_buffer(self):
        pass
    def write(self, data):
        self.writes.append(data)
        return len(data)
    def read(self, _):
        return next(self.chunks, b'')
    def close(self):
        self.closed = True


class TransportTests(unittest.TestCase):
    def transport(self, chunks):
        serial = SerialFixture(chunks)
        ticks = iter(i / 100 for i in range(10000))
        return ATTransport('mock', factory=lambda *a, **k: serial,
                           timeout=.1, clock=lambda: next(ticks)), serial

    def test_fragmented_exact_terminator_and_echo(self):
        transport, serial = self.transport([b'ATI\r\nBOOK\r\nO', b'K\r\n'])
        with transport:
            self.assertEqual(transport.query('ATI'), ['BOOK'])
        self.assertEqual(serial.writes, [b'ATI\r'])
        self.assertTrue(serial.closed)

    def test_partial_response_times_out(self):
        transport, serial = self.transport([b'EG25\r\n'])
        with transport, self.assertRaisesRegex(TransportError, 'timed out'):
            transport.query('ATI')
        self.assertTrue(serial.closed)

    def test_exact_error_and_cme_error(self):
        for error in (b'ERROR\r\n', b'+CME ERROR: SIM failure\r\n'):
            transport, _ = self.transport([error])
            with transport, self.assertRaisesRegex(TransportError, 'rejected'):
                transport.query('ATI')

    def test_no_arbitrary_commands_or_injection(self):
        transport, serial = self.transport([])
        with transport:
            for command in ('AT+EGMR=1,7,"123"', 'ATI\rAT+CFUN=1,1'):
                with self.assertRaises(TransportError):
                    transport.query(command)
            with self.assertRaises(TransportError):
                transport.set_usbnet('1\rAT+CFUN=1,1')
        self.assertEqual(serial.writes, [])

    def test_response_size_limit(self):
        transport, _ = self.transport([b'x' * 33000])
        with transport, self.assertRaisesRegex(TransportError, 'size limit'):
            transport.query('ATI')

    def test_short_write_poisoned_without_read(self):
        transport, serial = self.transport([b'OK\r\n'])
        serial.write = lambda _: 1
        with transport:
            with self.assertRaisesRegex(TransportError, 'Incomplete'):
                transport.query('ATI')
            with self.assertRaisesRegex(TransportError, 'reopening'):
                transport.query('ATI')

    def test_timeout_cannot_consume_late_ok_on_next_command(self):
        transport, serial = self.transport([b'partial\r\n'])
        with transport:
            with self.assertRaisesRegex(TransportError, 'timed out'):
                transport.query('ATI')
            serial.chunks = iter([b'OK\r\n'])
            with self.assertRaisesRegex(TransportError, 'reopening'):
                transport.query('AT+CGMM')
        self.assertEqual(len(serial.writes), 1)

    def test_completed_error_allows_next_query(self):
        transport, serial = self.transport([b'ERROR\r\n', b'EG25\r\nOK\r\n'])
        with transport:
            with self.assertRaisesRegex(TransportError, 'rejected'):
                transport.query('AT+CPIN?')
            self.assertEqual(transport.query('AT+CGMM'), ['EG25'])


if __name__ == '__main__':
    unittest.main()
