**JinjaRope** provides an entry-points based extension mechanism.

By declaring an extension point in a library, the JinjaRope environment can get modified easily.

``` toml
[project.entry-points."jinjarope.environment"]
my_extension = "my_library:setup_env"
```

`setup_env` (or your function name of choice) must take one argument, a **JinjaRope** Environment. On each Environment instanciation,
that method will get called and can extend the filters / tests namespace, add extensions etc.

``` py
def setup_env(env: jinjarope.Environment):
    env.do_something_you_want()
    # for auto-adding jinja file content:
    file = jinjarope.JinjaFile("my_jinja_file.toml")
    env.load_jinja_file(file)
```

!!! note
    Since **JinjaRope** already provides a lot of filters etc out-of-the-box, it is recommended
    to assign a custom prefix to additional filters / tests.


As an example, [MkNodes](https://phil65.github.io/mknodes) provides an entry point to add a large amount of Markdown filters
to the environment.
