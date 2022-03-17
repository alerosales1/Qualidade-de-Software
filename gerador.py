import json 
import os
import jinja2 

with open('teste.json', 'r') as f:
    data = json.load(f)
    
classes = dict()  # Guarda os nomes das classes
alt_names = dict() # Guarda os nomes para criação de classes

def generate_java_objects(data, old_key=''):
    # Gera recursivamente as classes e seus respectivos objetos
    global classes, alt_names
    
    if (type(data) == list): data = data[0]

    if (type(data) == dict and data.keys() == False): return # Se não houver elementos dentro, então é variável

    for key in data.keys(): # Se houver elementos dentro
        if (key not in classes.keys()): classes[key] = set() # Se a classe ainda não foi adicionada em classes, adiciona
        if (old_key): # Se a old_key possuir valor, então está dentro da recursão e não é o primeir caso
            classes[old_key] |= {key} # Atualiza o elemento dentro do dicionário do objeto da classe
            alt_names[old_key] = old_key.lower() + 's' # Gera o nome alternativo para criar arrays
                    
        if type(data[key]) == dict: # Se for uma classe, entra no dicionário e gera seus valores
                generate_java_objects(data[key], key)
        
        if type(data[key]) == list: # Se for uma lista, realiza a operação sobre cada um dos elementos
                for i in data[key]: generate_java_objects(i, key)

def generate_code_with_jinja():
    global classes, alt_names # Variáveis globais
    model = open('template_class').read() # Lê o template para gerar as classes
    
    template = jinja2.Template(model)
    
    c = set()
    c.update(classes.keys()) # Pega os nomes das classes
    c.intersection_update(alt_names) # Pega a interseção com alt_names, que possui apenas nome das classes
    code = [] # Código que será gerado
    
    for classe in sorted(list(c)):
        # Filtra as subclasses dentro de cada classe
        subclasses = set() 
        subclasses.update(classes[classe])
        subclasses.intersection_update(c)
        
        # Se não houver subclasses para um elemento, então não gera classes
        if subclasses == set():
            code.append(template.render(nome_classe=classe, strs=classes[classe]))
        else:
            # Caso contrário, evita que a classe seja assinalada como String e ArrayList
            strs = set(classes[classe])
            strs.difference_update(c)
            # Gera cada subclasse
            for sub in list(subclasses):
                code.append(template.render(nome_classe=classe, strs=list(strs), c=list(subclasses), alt_name=alt_names[sub]))
        code.append('\n')

    # Template para gerar o código com a main
    code_model = open('template_body_code').read()
    code_template = jinja2.Template(code_model)
    generated_code = code_template.render(classes=''.join(code))
    
    return generated_code # Retorna o código gerado
    
def write_and_compile(code):
    # Escreve o código no arquivo
    with open('Programa.java', 'w') as f: f.write(code)
    
    # Compila o código
    #os.system('javac *.java')

if __name__ == '__main__':
    os.system('pip install Jinja2')
    generate_java_objects(data)

    code = generate_code_with_jinja()
    print('Código gerado:\n')
    print(code)
    print(classes)
    
    write_and_compile(code)
