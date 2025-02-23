def snake_to_camel(snake_str):
    words = snake_str.split('_')
    camel_case = words[0] + ''.join(word.capitalize() for word in words[1:])
    return camel_case

snake_str = "hello_world_example"
camel_str = snake_to_camel(snake_str)
print(camel_str)
