#

## Libs

- `mock` is a library for testing in Python. It allows you to replace parts of your system under test with mock objects and make assertions about how they have been used.
- `nose` extends unittest to make testing easier.


## Steps

1. Before you write any tests, you need to know what to expect from the API.
2. You are now prepared to make your second assumption—you know what to expect the data to look like.
3. You should pull the code out of your test and refactor it into a service function that encapsulates all of that expected logic.

##

- `@patch()` - Provide it a path to the function you want to mock. The function is found, `patch()` creates a Mock object, and the real function is temporarily replaced with the mock.

## Others

－封装成测试类的好处：
    1. Moving common test functions to a class allows you to more easily test them together as a group. You can tell nose to target a list of functions, but it is easier to target a single class.
    2. Common test functions often require similar steps for creating and destroying data that is used by each test. These steps can be encapsulated in the setup_class() and teardown_class() functions respectively in order to execute code at the appropriate stages.
    3. You can create utility functions on the class to reuse logic that is repeated among test functions. Imagine having to call the same data creation logic in each function individually. What a pain!
- 对于频繁更新的 API，要确保测试使用的数据与第三方服务器返回的一致，恰当的做法是：比较两个数据结构
－何时应该进行 Mock 数据是否正确？该测试应该放在自动测试之外，并且应当频繁地测试。一个可选的方案是，使用环境变量作为触发。

```python
import os

SKIP_REAL = os.getenv("SKIP_REAL", False)
```

```bash
$ export SKIP_REAL=True
```
