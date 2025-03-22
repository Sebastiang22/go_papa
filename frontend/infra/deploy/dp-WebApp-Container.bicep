param staticWebAppName string
param location string = resourceGroup().location
param skuName string = 'Free'

resource staticSite 'Microsoft.Web/staticSites@2022-03-01' = {
  name: staticWebAppName
  location: location
  sku: {
    name: skuName
    tier: skuName
  }
  properties: {
    // Si utilizas despliegue local (upload), estos valores pueden quedar vacíos.
    repositoryUrl: ''
    branch: ''
    buildProperties: {
      // Ubicación del código fuente (por ejemplo, la raíz si ya está compilado)
      appLocation: '/'
      // Si tienes un API integrado, indícalo; si no, déjalo vacío
      apiLocation: ''
      // Carpeta con los archivos compilados que serán servidos
      appArtifactLocation: 'build'
    }
  }
}
