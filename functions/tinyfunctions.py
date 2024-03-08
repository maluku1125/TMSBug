import random

def probably(chance):
    return random.random() < chance

def RollDice(expression, modifier, compare):

    parts = expression.split('d')
    num_rolls = int(parts[0])
    sides = int(parts[1])

    # 擲骰
    results = [random.randint(1, sides) for _ in range(num_rolls)]
    total = sum(results)
    response1 = f"> 擲骰 {num_rolls}d{sides}"
    response2 = ""
    response3 = ""

    if modifier:
        # +5、-2、*3、/2
        operator = modifier[0]
        value = int(modifier[1:])
 
        if operator == '+':
            total = total + value
        elif operator == '-':
            total = total - value
        elif operator == '*':
            total = total * value
        elif operator == '/':
            total = total / value

        response2 = f"{operator}{value}"

    if compare:
        # >、<、>=、<=
        if compare.startswith('>='):
            operator = '>='
            value = int(compare[2:])
        elif compare.startswith('<='):
            operator = '<='
            value = int(compare[2:])
        elif compare.startswith('>'):
            operator = '>'
            value = int(compare[1:])
        elif compare.startswith('<'):
            operator = '<'
            value = int(compare[1:])
        else:
            operator = None
            value = None

        if operator is not None:
            if operator == '>=':
                success = total >= value
            elif operator == '<=':
                success = total <= value
            elif operator == '>':
                success = total > value
            elif operator == '<':
                success = total < value           

        response3 = f" ({'成功' if success else '失敗'})"
    
    rollresult = f'{response1}{response2}\n結果：{total}{response3}'


    return rollresult