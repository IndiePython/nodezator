
def option_tray_test(

      param1: bool               = None,
      param2: (None, bool)       = True,
      param3: (type(None), bool) = None,

      param4: {
        'widget_name'   : 'option_tray',
        'widget_kwargs' : {
          'options' : [False, None, True]
        },
        'type': (None, bool)
      } = None,

      param5: {
        'widget_name'   : 'option_tray',
        'widget_kwargs' : {
          'options' : ['Red', 'Green', 'Blue']
        },
        'type': str
      } = 'Red',

      param6: {
        'widget_name'   : 'option_tray',
        'widget_kwargs' : {
          'options' : [1, 10, 100, 500]
        },
        'type': int
      } = 100

    ):
    """Return tuple with received arguments."""
    return (
      param1,
      param2,
      param3,
      param4,
      param5,
      param6
    )

main_callable = option_tray_test
