param containerAppName string
param containerRegistryName string
param imageName string

resource acr 'Microsoft.ContainerRegistry/registries@2021-06-01-preview' existing = {
  name: containerRegistryName
}

resource containerApp 'Microsoft.App/containerApps@2022-03-01' existing = {
  name: containerAppName
}

resource containerAppUpdate 'Microsoft.App/containerApps/revisions@2022-03-01' = {
  parent: containerApp
  name: 'current'
  properties: {
    template: {
      containers: [
        {
          name: containerAppName
          image: '${acr.name}.azurecr.io/${imageName}'
        }
      ]
    }
  }
}
