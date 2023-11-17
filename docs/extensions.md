**JinjaRope** provides an entry-points based extension mechanism.

By declaring an extension point in a library, the JinjaRope environment can get modified easily.

``` toml
[project.entry-points."jinjarope.environment"]
my_extension = "my_library:setup_env"
```

`setup_env` must take one argument, a **JinjaRope** Environment. On each Environment instanciation,
that method will get called and can extend the filters / tests namespace, add extensions etc.

!!! note
    Since **JinjaRope** already provides a lot of filters etc out-of-the-box, it is recommended
    to assign a custom prefix to additional filters / tests.
