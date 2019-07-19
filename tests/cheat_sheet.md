
###UNITTEST - CHEAT SHEET

####Running a single test case or test method:

If using pipenv, start pipenv shell first: 

    pipenv shell

In parent folder type:

    python -m unittest test.test_search.TestName

####Running a single test module:

In parent folder type:
    
    python -m unittest test.test_search

####Run all tests:

    python -m unittest discover

###UNITTEST - ASSERTION - API

####Equal
a == b

    assertEqual(a, b)

####Not Equal
a != b

    assertNotEqual(a, b)

#### True
bool(x) is True

    assertTrue(x)

#### False
bool(x) is False

    assertFalse(x)

#### Is
a is b

    assertIs(a, b)

#### Is not
a is not b

    assertIsNot(a, b)

#### Is none
x is None

    assertIsNone(x)

#### Is not none
x is not None

    assertIsNotNone(x)

#### In
a in b

    assertIn(a, b)

#### Not in
a not in b

    assertNotIn(a, b)

#### Is instance
isinstance(a, b)

    assertIsInstance(a, b)

#### Not instance
not isinstance(a, b)

    assertNotIsInstance(a, b)
