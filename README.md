![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![AmazonDynamoDB](https://img.shields.io/badge/Amazon%20DynamoDB-4053D6?style=for-the-badge&logo=Amazon%20DynamoDB&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![image](https://img.shields.io/badge/Swagger-85EA2D?style=for-the-badge&logo=Swagger&logoColor=ffffff)
![YAML](https://img.shields.io/badge/yaml-%23ffffff.svg?style=for-the-badge&logo=yaml&logoColor=151515)
# Projeto de API em Rest

Este é um projeto de exemplo de uma API REST desenvolvido aproveitando das soluções Serverless da AWS. Este projeto é um desafio do curso re/start da Generation em parceria com a AWS.

## Link de acesso ao projeto

https://d2yg3mic8ob00y.cloudfront.net/

## Sumário:

- [Sobre o Projeto](#sobre-o-projeto)
- [Tecnologias](#tecnologias)
- [Setup](#setup)
- [Abordagem](#abordagem)
- [License](#licenças-de-utilização)

## Sobre o Projeto

A aplicação consiste em uma api para realizar operações básicas de um CRUD (Create, Read, Update, Delete) em três tabelas, usuários, temas e postagens. Toda a infraestrutura é provisionada automaticamente utilizando o AWS CDK (Cloud Development Kit) escrito em Python, o que facilita a criação e gerenciamento da infraestrutura como código. Além disso, a aplicação é documentada utilizando o Swagger/OpenAPI para facilitar os testes e a compreensão das rotas disponíveis.

![blogapi](https://github.com/oicaroabreu/aws-cdk-blog-serverless/assets/136408366/a68e047a-1a76-4086-82eb-978362f651e2)


## Tecnologias

Este projeto faz uso de diversas tecEste projeto faz uso de diversas tecnologias e ferramentas, incluindo:

- **AWS CDK**: Cloud Development Kit, para provisionamento de infraestrutura na AWS.

- **AWS API Gateway**: Serviço da AWS para criação, publicação, manutenção, monitoramento e proteção de APIs.

- **AWS S3**: Simple Storage Service, para armazenamento de objetos na nuvem.

- **AWS CloudFront**: Serviço de CDN (Content Delivery Network) da AWS.

- **AWS Cognito**: Serviço de autenticação e autorização de usuários da AWS.

- **AWS Lambda Function**: Serviço de computação serverless da AWS.

- **Lambda Layers**: Uma maneira de compartilhar código e recursos entre funções Lambda.

- **AWS DynamoDB**: Banco de dados NoSQL totalmente gerenciado pela AWS.

- **Poetry**: Ferramenta para gerenciamento de dependências e ambientes virtuais em projetos Python.

- **Swagger**: Framework de código aberto para documentação de APIs RESTful.


## Setup

### Utilizar o Projeto Localmente

Para utilizar iar o projeto localmente, siga as instruções abaixo:

1. **Clone o Repositório**: Faça uma cópia deste repositório em sua máquina local.

2. **Configuração do Ambiente Python**: Certifique-se de que você possui um ambiente virtual Python configurado. Use algum gerenciador de pacotes para instalar as dependências.

   > Com `pip`:
   >
   > ```bash
   > python -m venv .venv
   > pip install -r requirements.txt
   > ```
   >
   > Ou `poetry`:
   >
   > ```bash
   > poetry install
   > ```

3. **Certifique-se que tem o Docker instalado**: O pacote `aws-cdk-aws-lambda-python-alpha` faz uso do Docker para preparar as funções Lambda com Python e suas `Lambda Layer` para deploy na AWS.

4. **Sintetize o template CloudFormation**: Para conferir erros na infraestrutura e gerar o template CloudFormation:

   ```bash
   cdk synth
   ```

5. **Prepare o build e faça o deploy**: para preparar o artefato das funções Lambda e suas camadas e executar o deploy da infraestrutura:

   ```bash
   cdk build && cdk deploy
   ```

5. Copie o endereço da API do output no CLI

## Abordagem

- **Arquitetura Serverless**: Utilizamos uma abordagem serverless para desenvolver a aplicação, o que permite escalabilidade automática e redução de custos ao eliminar a necessidade de gerenciar servidores.

- **Infraestrutura como código**: Toda a infraestrutura é definida e gerenciada como código, facilitando a implantação e o versionamento por meio do AWS CDK.

- **Content Delivery Network**: Utilizamos o Amazon CloudFront como CDN para melhorar a entrega de conteúdo, garantindo alta disponibilidade e baixa latência para os usuários finais.

- **Commits Semânticos**: Adotamos a prática de commits semânticos para manter um histórico de alterações legível e informativo.

## LICENÇAS DE UTILIZAÇÃO

Este projeto é distribuído sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para obter detalhes completos sobre os termos da licença.

Sinta-se à vontade para contribuir com melhorias ou correções para este projeto. Basta abrir uma issue ou enviar um pull request.
