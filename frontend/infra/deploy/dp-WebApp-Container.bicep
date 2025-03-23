param webAppName string
param containerRegistryName string
param imageName string

resource acr 'Microsoft.ContainerRegistry/registries@2021-06-01-preview' existing = {
  name: containerRegistryName
}

resource webApp 'Microsoft.Web/sites@2021-02-01' existing = {
  name: webAppName
}

resource webAppConfig 'Microsoft.Web/sites/config@2021-02-01' = {
  parent: webApp
  name: 'web'
  properties: {
    appSettings: [
      {
        name: 'DOCKER_REGISTRY_SERVER_URL'
        value: 'https://${acr.name}.azurecr.io'
      }
      {
        name: 'DOCKER_REGISTRY_SERVER_USERNAME'
        value: acr.listCredentials().username
      }
      {
        name: 'DOCKER_REGISTRY_SERVER_PASSWORD'
        value: acr.listCredentials().passwords[0].value
      }
    ]
    linuxFxVersion: 'DOCKER|${acr.name}.azurecr.io/${imageName}'
  }
}
