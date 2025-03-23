<script setup>
import { ref, onMounted } from 'vue'
import { sharedState } from './state'

import MainChat from './views/MainChat.vue';
import Loader from './views/AuthLoader.vue'

const loaderMessage = ref('Autenticándose ...')
const loading = ref(true)

onMounted(async () => {

  ////  +++++++++++++++++++++++++++++++++
  ////               LOCAL
  //// +++++++++++++++++++++++++++++++++
  // // ESTO SIMULA LA AUTENTICACION
  const generateRandomHash = () => {
  return Math.random().toString(36).substring(2, 15);
  }

  const name = 'User Tars'//urlParams.get('name');
  const email = 'user_tars@outlook.com'//urlParams.get('email');
  const client = `chatweb-${generateRandomHash()}`;

  setTimeout(() => {
      sharedState.id = client;
      sharedState.name = name;
      loaderMessage.value = 'Casi listo ...'
      setTimeout(() => {
          loading.value = false
        }, 2000)
      }, 1000)

  ////  +++++++++++++++++++++++++++++++++
  ////                AZURE
  //// +++++++++++++++++++++++++++++++++
      // COMO DEBERIA SER LA AUTENTICACION
      
// const urlParams = new URLSearchParams(window.location.search);
// const email = urlParams.get('email');
// const name = urlParams.get('name');

// if (name && email) {
//     loaderMessage.value = 'Casi listo ...'
//     sharedState.id = email;
//     sharedState.name = name;
//     urlParams.delete('email')
//     const newUrl = `${window.location.pathname}?${urlParams.toString()}`
//     window.history.pushState({}, document.title, newUrl)
//     setTimeout(() => {
//       loading.value = false
//     }, 2000)

//   } else {

//     window.location.href = 'https://gopapa-backend.blueriver-8537145c.westus2.azurecontainerapps.io/api/auth/login';
//     // window.location.href = 'http://localhost:8000/api/auth/login';
//   }
});
</script> 
<!-- <script setup>
import { ref, onMounted } from 'vue'
import { sharedState } from './state'

import MainChat from './views/MainChat.vue';
import Loader from './views/AuthLoader.vue'

const loaderMessage = ref('Cargando ...') // Cambié el mensaje para que no diga "Autenticándose"
const loading = ref(false) // 🔹 Desactivamos el estado de carga para que no bloquee la app

onMounted(() => {
  // 🔹 Aquí eliminamos la autenticación y permitimos el acceso libre
  sharedState.id = "guest"; // Usuario genérico o puedes dejarlo vacío
  sharedState.name = "Invitado"; // Opcional

});

</script> -->
<template>
    <transition name="fade" mode="out-in" v-if="loading">
      <Loader :message="loaderMessage" />
    </transition>
    <MainChat />

</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 1s ease-in-out;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
