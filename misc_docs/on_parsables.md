# On `Parsable` and `GenericParsable`:

The `GenericParsable` class automatically parses properties of its subclasses which follow a dedicated pattern. Any subclass of `GenericParsable` can have a valid and unique property "foo" provided the following three implementations are made for it:



```python
@property
def has_foo(self) -> bool: 
    ...


@property
def foo(self) -> T: 
    ...


@foo.setter
def foo(self, input_value): 
    ...
```

If `foo` is not settable then the setter may be omitted. If `foo` is guaranteed to always contain a valid
value then `has_foo` can be omitted. 
If an update routine is needed for a particular property then an additional method can be defined:

```python
def update_foo(self, input_value): 
    ...
```

When defined, `update_foo`, will be used in place of the `foo` setter when `update()` is called on this class.
In addition, each attribute must fall into one of the predefined categories of parsing types. The categories are
as follows:
- Serializable:
    Attributes that are primitive type such as numbers, strings, list of string or numbers, dictionary of
    strings or numbers, or entities that have a method `tolist()` that converts its contents to a list of
    numbers or strings such as numpy arrays. All of these types are basic types that the JSON encoder handles
    by default. To register a property as serializable, the subclass must append the property name onto
    the end of the list `_serializable_attributes`.
- Enum:
    Attributes that are simple enums, not list of enums or dict of enums. This parsing routine converts the
    enums to and from strings using their name property. To register a property for enum parsing, the subclass
    must append the property name onto the end of the list `_enum_attributes`. In the subclass implementation
    the property setter functions should provide the `@enum_setter()` decorator for efficient deserialization.
- Parsable:
    Attributes that are objects whose type is derived from the base class `Parsable`. This allows those
    attributes to have a contained parsing routine which outputs a dictionary, which maps their internal
    attribute names to their values. This can create a chain of hierarchical parsing of classes. To register a
    property as a `Parsable`, the subclass must append the property name onto the end of the list
    `_parsable_attributes`. In the subclass implementation the property setter functions should provide the
    `@parsable_setter()` decorator for efficient deserialization.
- Dictionary of Parsables:
    Attributes which contain a dictionary mapping of serializable keys to parsable objects as their values.
    To register a property for as a dictionary of parsables, the subclass must append the property name onto
     the end of the list `_dict_of_parsables`.
- List of Parsables:
    Attributes which contain an ordered list of parsable objects. To register a property as a list of
    parsables, the subclass must append the property name onto the end of the list `_list_of_parsables`.
- Specialized:
    All other types of attributes that require specialized encoding and decoding functions. For these
    attributes they much have implementations of functions named `foo_encode()` and `foo_decode(input)` for
    the attribute named `foo`. The function `foo_encode()` would return the serializable representation of `foo`
    while `foo_decode(input)` would take the serialized `input` and set its deserialized representation to
    `foo`. To register a property for specialized parsing, the subclass must append the property name onto the
    end of the list `_specialized_attributes`.
The proper way of registering properties of a subclass of `GenericParsable` is demonstrated below:


```python
class FooClass(GenericParsable)
    def __init__(self, *args, **kwargs):
        # --- init the parent ---
        super().__init__(*args, **kwargs)
        # --- set up the parsable attributes ---
        self._serializable_attributes.extend(['foo'])
        self._specialized_attributes.extend(['bar'])
        # --- set components ---
        self.foo = kwargs.get('foo')
        self.bar = kwargs.get('bar')
    @property
    def has_foo(self) -> bool:
        return self._foo is not None


    @property
    def foo(self) -> int:
        if self._foo is None:
            loghandler.log_and_raise(AttributeError, "The foo has not been set.", record_location=True)
        return self._foo
    
    
    @foo.setter
    def foo(self, input_value):
        if input_value is None or (isinstance(input_value, int) and input_value >= 0):
            self._foo = input_value
        else:
            loghandler.log_and_raise(TypeError, "Invalid type [", type(input_value), "].", record_location=True)
    
    
    @property
    def has_bar(self) -> bool:
        return self._bar is not None
    
    
    @property
    def bar(self) -> Bar:
        if self._bar is None:
            loghandler.log_and_raise(AttributeError, "The bar has not been set.", record_location=True)
        return self._bar
    
    
    @bar.setter
    def bar(self, input_value):
        if input_value is None or isinstance(input_value, Bar):
            self._bar = input_value
        else:
            loghandler.log_and_raise(TypeError, "Invalid type [", type(input_value), "].", record_location=True)
    
    
    def bar_encode(self):
        return str(self.bar)
    
    
    def bar_decode(self, input_value):
        self.bar = Bar.from_str(input_value)
```

Finally, some subclasses may require that attributes are parsed in a specific order. To enable this, just append the attributes that are to be parsed first to the list `_desired_order_of_parsing` in the order that the attributes should be parsed. Attributes that do not require a specific order of parsing can be omitted from this list. They will be parsed, in no specific order, after all registered attributes in `_desired_order_of_parsing` have been parsed. The attributes registered in `_desired_order_of_parsing` must also be registered in one of the category lists. Registering an attribute that is not also registered in any category will cause the parsing routine to raise an exception.