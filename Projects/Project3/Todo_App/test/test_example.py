import pytest

# test integers
def test_equal_or_not_equal():
    assert 3 == 3

# test instance
def test_is_instance():
    assert isinstance("this is string",str)
    assert not isinstance("10",int)

# test booleans
def test_booleans():
    validated = True
    assert validated is True
    assert ('True' == 'False') is False

# test greater than or less than
def greater_and_less_than():
    assert 7>2
    assert 4 < 10

# test types
def test_types():
    assert type('Hello' is str)
    assert type("World" is not int)

# test types
def test_list_types():
    num_list = [1,2,3,4]
    any_list = [False,False]
    assert 1 in num_list
    assert 7 not in num_list
    assert all(num_list)
    assert not any(any_list)

# pytest object - using fixtures
class Student:
    def __init__(self,fname,lname,major,years):
        self.fname = fname
        self.lname = lname
        self.major = major
        self.years = years

# old way
def test_person_initialization():
    p = Student('John','Doe','CS',3)
    assert p.fname == 'John','First name should be John'
    assert p.lname == 'Doe','Last name should be Doe'
    assert p.major == 'CS'
    assert p.years == 3

# using fixtures
@pytest.fixture
def default_person():
    return Student('John','Doe','CS',3)

def test_person_fixture_ini(default_person):
    assert default_person.fname == 'John','First name should be John'
    assert default_person.lname == 'Doe','Last name should be Doe'
    assert default_person.major == 'CS'
    assert default_person.years == 3