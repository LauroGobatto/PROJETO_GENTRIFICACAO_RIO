import subprocess

def rodar_script(nome_script):
    print(f" Rodando o código: {nome_script}")
    resultado = subprocess.run(['python', nome_script], capture_output = True, text=True)
    if resultado.returncode == 0:
        print(f"Sucesso: {nome_script}")
    else:
        print(f"Erro em {nome_script}: {resultado.stderr}")
        exit(1)

if __name__ == "__main__":
    #SCRAPPING
    rodar_script('src/collectors/WebScrappingFinal.py')

    #TRATAMENTO DOS DADOS
    rodar_script('src/processing/Tratamento_dados.py')

    #COORDENADAS
    rodar_script('output/scripts_graficos/GRÁFICO_DE_CALOR.py')
    
    #MODELO
    rodar_script('src/models/MODELO.py')

    #MIGRAR PARA SQL
    rodar_script('migrar_sql.py')