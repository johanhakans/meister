import unittest
import meister.test.aws

def main():
    print "Running tests"
    suite = unittest.TestLoader().loadTestsFromTestCase(meister.test.aws.AWSConnectionTest)
    unittest.TextTestRunner(verbosity=2).run(suite)

main()
