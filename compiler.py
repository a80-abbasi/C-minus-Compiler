# Maziar Shamsipour 98101844
# Ali Abbasi 98105879


from scanner import Scanner

input_file = open('input.txt', 'r')
scanner = Scanner(input_file)
tokens_file = open('tokens.txt', 'w')
first_token_not_given = True
line_number = scanner.line_number

while True:
    token_type, token_string = scanner.get_next_token()
    # print(token_type, token_string)
    if token_type is None:
        break

    if token_type != 'WHITESPACE' and token_type != 'COMMENT':
        if first_token_not_given:
            first_token_not_given = False
            tokens_file.write(f'{scanner.line_number}.\t')
        elif line_number != scanner.line_number:
            tokens_file.write(f'\n{scanner.line_number}.\t')
        tokens_file.write(f"({token_type}, {token_string}) ")
        line_number = scanner.line_number

tokens_file.write(f'\n')
scanner.close_files()
tokens_file.close()
input_file.close()