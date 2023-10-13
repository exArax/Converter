def generate(nodelist, application):
    json_template = {}

    for x in nodelist:
        if 'ACCORDION.Cloud_Framework' in x.get_type():
            actions = x.get_actions()
            for action in actions:
                components = action.get('components')
                componentList = []
                for component in components:
                    componentList.append(application + "-" + component)
                action.update(components=componentList)
            json_template['action_set'] = []
            json_template['action_set'].append(actions)

    return json_template
