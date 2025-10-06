from django import template
register = template.Library()

@register.filter(name='formata_tel')
def formata_tel(numero):
    if len(numero) == 10:
        first = numero[0:2]
        second = numero[2:6]
        third = numero[6:10]
        return '(' + first + ')' + ' ' + second + '-' + third
    else:
        first = numero[0:2]
        second = numero[2:7]
        third = numero[7:11]
        return '(' + first + ')' + ' ' + second + '-' + third

@register.filter(name='formata_cpf')
def formata_cpf(numero):
    first = numero[0:3]
    second = numero[3:6]
    third = numero[6:9]
    fourth = numero[9:11]
    return first + '.' + second + '.' + third + '-' + fourth
