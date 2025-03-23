import axios from 'axios';
import { sharedState } from './state'

const apiClientMultipart = axios.create({
  // baseURL: 'http://localhost:8000/api/agent/chat',
  baseURL: 'https://gopapa-backend.blueriver-8537145c.westus2.azurecontainerapps.io/api/agent/chat',
  //baseURL: '/api',
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});
const apiClientCommon = axios.create({
  // baseURL: 'http://localhost:8000/api/agent/chat',
  baseURL: 'https://gopapa-backend.blueriver-8537145c.westus2.azurecontainerapps.io/api/agent/chat',
  //baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default {
  async requestCHAT(data) {
    const response = await apiClientCommon.post('/message', data);
    return response.data
  },
  // async requestWhisper(audio) {
  //   const response = await apiClientMultipart.post('/audio', audio);
  //   return response.data
  // },
  async requestAttachment(attachment) {
    const response = await apiClientMultipart.post('/attachment', attachment);
    return response.data
  },
  async requestVote(msg_id,vote) {
    const requestData = {
      id: msg_id,
      thread_id: sharedState.user_id,
      rate: vote,
    }
    console.log("Datos enviados en requestVote",requestData)
    const response = await apiClientCommon.post('/vote', requestData);
    return response.data
  },
  async requestSession(convesationI) {
    const response =apiClientCommon.get()
  }
};