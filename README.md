
 **Pré-requisites**: Compartment, vcn e subnet container registry.
 
### Passo 1: Configurar o Ambiente Local

1. **Instalar OCI CLI**:
   Siga as instruções na [documentação da OCI CLI](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm).
   Configure no Vscode oci credencial e uma chave de API chaves, caso ja tenha criado copie para sua pasta  o arquivo de configuração (~/.oci/oci_key.pem).
   Configure localmente oci id user e tenancy.
   Corrigir Permissões da pasta onde esta a chave
   
   ```bash
   oci setup repair-file-permissions --file /home/joyce/.oci/sessions/DEFAULT/oci_api_key
   ```

3. **Instalar Fn CLI**:
   O Fn Project é usado para desenvolver, testar e deployar funções para Oracle Functions.
   Siga as instruções na [documentação do Fn Project](https://github.com/fnproject/cli#install).

### Passo 2: Criar e Configurar uma Oracle Function

1. **Configurar o Fn Project para OCI**:
   Certifique-se de que o Fn CLI está configurado para usar o Oracle Functions.

   ```bash
   fn update context oracle.compartment-id <compartment-ocid>
   fn update context oracle.profile DEFAULT
   fn update context registry <region-key>.ocir.io/<repo-name>
   ```

   Substitua `<compartment-ocid>`, `<region-key>` e `<repo-name>` pelos valores apropriados.

   Neste passo siga as instruções do "Getting started" ate a etapa 5.

3. **Criar uma Aplicação de Oracle Functions**:
   No Console OCI, navegue para "Developer Services" > "Functions" e crie uma nova aplicação.

4. **Inicializar a Função**:
   Use o CLI do Fn Project para inicializar a função.

   ```bash
   fn init --runtime python fn-create-tenancy
   cd fn-create-tenancy
   ```

5. **Escrever a Função Python**:
   Substitua o conteúdo de `func.py` pelo seguinte:

   ```python
   import oci
   import json

   def handler(ctx, data: str = None):
       config = oci.config.from_file()

       organizations_client = oci.organizations.OrganizationsClient(config)

       body = json.loads(data)
       
       create_child_tenancy_details = oci.organizations.models.CreateChildTenancyDetails(
           compartment_id=body["compartment_id"],
           tenancy_name=body["tenancy_name"],
           tenancy_description=body["tenancy_description"],
           home_region=body["home_region"],
           admin_email=body["admin_email"]
       )

       response = organizations_client.create_child_tenancy(create_child_tenancy_details)
       
       return json.dumps({"tenancy_id": response.data.tenancy_id})
   ```

6. **Configurar o Dockerfile**:
   Verifique se o `Dockerfile` está configurado corretamente:

   ```dockerfile
   FROM fnproject/python:3.8

   ADD . /function/
   WORKDIR /function/

   RUN pip3 install --target /function/ oci

   CMD ["func.py"]
   ```

7. **Empurrar a Imagem Docker para o Registro da OCI**
  1. Siga apartir do passo 6:
   Log into the Registry using the Auth Token as your password
   
   ```bash
   docker login -u 'xxxxxx/xxxx@xxxx.com.br' gru.ocir.io
   ```
  2. Entre com a senha (passos 7)
  3. Construir a Imagem Docker no diretório contendo o Dockerfile,
     
   ```bash
   docker build -t gru.ocir.io/<tenancy-namespace>/<registtrirepo>:tag
   ```

   ```bash
   docker push gru.ocir.io/<tenancy-namespace>/<registtrirepo>:tag
   ```

9. **Deployar a Função**:
   Use o CLI do Fn Project para empacotar e deployar sua função na OCI:

   ```bash
   fn -v deploy --app <app-name>
   ```

   Substitua `<app-name>` pelo nome da aplicação criada na OCI.

### Passo 3: Configurar o API Gateway

1. **Criar um API Gateway**:
   No Console OCI, navegue para "Developer Services" > "API Gateway" e crie um novo API Gateway.

2. **Criar uma API**:
   Dentro do API Gateway, crie uma nova API e configure um endpoint que aponte para sua função.

3. **Configurar o Endpoint da API**:
   No API Gateway, configure um recurso e uma rota para a função que você criou. O método HTTP deve ser POST, e a função deve ser a que você acabou de deployar.

### Passo 4: Testar a API

1. **Chamar a API**:
   Os dados como compartment_id, tenancy_name, tenancy_description, home_region, e admin_email que você mencionou são necessários para a criação do tenancy e devem ser 
    fornecidos pelo usuário ao chamar a API. Eles não são gerados automaticamente; você precisa fornecer esses valores na solicitação à sua API.
   Use `curl` ou qualquer cliente HTTP para chamar sua API.
   Exemplo de Configuração de Corpo da Requisição
   Quando você faz a chamada à API para criar um tenancy, você deve enviar esses dados no corpo da solicitação (payload). Aqui está um exemplo de como isso pode ser feito 
    usando curl:

   ```bash
   curl -X POST https://<api-gateway-endpoint>/<resource-path> \
       -H "Content-Type: application/json" \
       -d '{
           "compartment_id": "ocid1.compartment.oc1..example",
           "tenancy_name": "NewTenancyName",
           "tenancy_description": "Description of the new tenancy",
           "home_region": "us-phoenix-1",
           "admin_email": "admin@example.com"
       }'
   ```

### Resumo dos Passos

1. Configurar o ambiente local com OCI CLI e Fn CLI.
2. Criar uma aplicação e função no Oracle Functions.
3. Escrever e empacotar a função em Python.
4. Deployar a função na OCI usando o Fn CLI.
5. Configurar um API Gateway para expor a função como uma API.
6. Testar a API usando `curl` ou outro cliente HTTP.

Seguindo esses passos, você terá uma API na OCI que cria tenancies utilizando Python, Oracle Functions e API Gateway.
