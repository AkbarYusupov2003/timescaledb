import splay_data


def execute_register_task(period):
    print("execute_register_task", period)
    data = splay_data.get_data(splay_data.SIGNUP_URL, params={'period': period})
    # TODO add to db
    
