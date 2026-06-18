import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const photos = {
  list: (params = {}) => api.get('/photos/', { params }),
  simple: () => api.get('/photos/simple/'),
  get: (id) => api.get(`/photos/${id}/`),
  create: (data, config = {}) => api.post('/photos/', data, config),
  update: (id, data) => api.put(`/photos/${id}/`, data),
  patch: (id, data) => api.patch(`/photos/${id}/`, data),
  delete: (id) => api.delete(`/photos/${id}/`),
  addPerson: (id, data) => api.post(`/photos/${id}/add_person/`, data),
  getPeople: (id) => api.get(`/photos/${id}/people/`)
}

export const persons = {
  list: (params = {}) => api.get('/persons/', { params }),
  simple: () => api.get('/persons/simple/'),
  get: (id) => api.get(`/persons/${id}/`),
  create: (data) => api.post('/persons/', data),
  update: (id, data) => api.put(`/persons/${id}/`, data),
  patch: (id, data) => api.patch(`/persons/${id}/`, data),
  delete: (id) => api.delete(`/persons/${id}/`),
  addAlias: (id, data) => api.post(`/persons/${id}/add_alias/`, data),
  addMigration: (id, data) => api.post(`/persons/${id}/add_migration/`, data)
}

export const personInPhoto = {
  list: (params = {}) => api.get('/person-in-photo/', { params }),
  get: (id) => api.get(`/person-in-photo/${id}/`),
  create: (data) => api.post('/person-in-photo/', data),
  update: (id, data) => api.put(`/person-in-photo/${id}/`, data),
  patch: (id, data) => api.patch(`/person-in-photo/${id}/`, data),
  delete: (id) => api.delete(`/person-in-photo/${id}/`)
}

export const relationships = {
  list: (params = {}) => api.get('/relationships/', { params }),
  create: (data) => api.post('/relationships/', data),
  update: (id, data) => api.put(`/relationships/${id}/`, data),
  patch: (id, data) => api.patch(`/relationships/${id}/`, data),
  delete: (id) => api.delete(`/relationships/${id}/`)
}

export const aliases = {
  list: (params = {}) => api.get('/aliases/', { params }),
  create: (data) => api.post('/aliases/', data),
  update: (id, data) => api.put(`/aliases/${id}/`, data),
  patch: (id, data) => api.patch(`/aliases/${id}/`, data),
  delete: (id) => api.delete(`/aliases/${id}/`)
}

export const migrations = {
  list: (params = {}) => api.get('/migrations/', { params }),
  create: (data) => api.post('/migrations/', data),
  update: (id, data) => api.put(`/migrations/${id}/`, data),
  patch: (id, data) => api.patch(`/migrations/${id}/`, data),
  delete: (id) => api.delete(`/migrations/${id}/`)
}

export const memories = {
  list: (params = {}) => api.get('/memories/', { params }),
  get: (id) => api.get(`/memories/${id}/`),
  create: (data) => api.post('/memories/', data),
  update: (id, data) => api.put(`/memories/${id}/`, data),
  patch: (id, data) => api.patch(`/memories/${id}/`, data),
  delete: (id) => api.delete(`/memories/${id}/`),
  linkPhoto: (id, photoId) => api.post(`/memories/${id}/link_photo/`, { photo_id: photoId }),
  linkPerson: (id, personId) => api.post(`/memories/${id}/link_person/`, { person_id: personId })
}

export const conflicts = {
  list: (params = {}) => api.get('/conflicts/', { params }),
  get: (id) => api.get(`/conflicts/${id}/`),
  create: (data) => api.post('/conflicts/', data),
  update: (id, data) => api.put(`/conflicts/${id}/`, data),
  patch: (id, data) => api.patch(`/conflicts/${id}/`, data),
  resolve: (id, version, resolvedBy = '') => api.post(`/conflicts/${id}/resolve/`, { version, resolved_by: resolvedBy })
}

export const confirmations = {
  list: (params = {}) => api.get('/confirmations/', { params }),
  get: (id) => api.get(`/confirmations/${id}/`),
  create: (data) => api.post('/confirmations/', data),
  update: (id, data) => api.put(`/confirmations/${id}/`, data),
  patch: (id, data) => api.patch(`/confirmations/${id}/`, data),
  vote: (id, voter, vote) => api.post(`/confirmations/${id}/vote/`, { voter, vote })
}

export const stats = {
  get: () => api.get('/stats/')
}

export const clues = {
  list: (params = {}) => api.get('/clues/', { params }),
  get: (clueKey) => api.get(`/clues/${clueKey}/`),
  claim: (data) => api.post('/clues/claim/', data),
  stats: () => api.get('/clues/stats/')
}

export const tasks = {
  list: (params = {}) => api.get('/tasks/', { params }),
  get: (id) => api.get(`/tasks/${id}/`),
  create: (data) => api.post('/tasks/', data),
  update: (id, data) => api.put(`/tasks/${id}/`, data),
  patch: (id, data) => api.patch(`/tasks/${id}/`, data),
  delete: (id) => api.delete(`/tasks/${id}/`),
  myTasks: (params = {}) => api.get('/tasks/my_tasks/', { params }),
  claim: (id, data) => api.post(`/tasks/${id}/claim/`, data),
  unclaim: (id) => api.post(`/tasks/${id}/unclaim/`),
  submit: (id, data) => api.post(`/tasks/${id}/submit/`, data),
  review: (id, data) => api.post(`/tasks/${id}/review/`, data),
  submissions: (id) => api.get(`/tasks/${id}/submissions/`),
  stats: (params = {}) => api.get('/tasks/stats/', { params }),
  generate: (data) => api.post('/tasks/generate/', data)
}

export const taskSubmissions = {
  list: (params = {}) => api.get('/task-submissions/', { params }),
  get: (id) => api.get(`/task-submissions/${id}/`),
  create: (data) => api.post('/task-submissions/', data),
  update: (id, data) => api.put(`/task-submissions/${id}/`, data),
  patch: (id, data) => api.patch(`/task-submissions/${id}/`, data),
  delete: (id) => api.delete(`/task-submissions/${id}/`)
}

export const contributions = {
  list: (params = {}) => api.get('/contributions/', { params }),
  get: (id) => api.get(`/contributions/${id}/`),
  ranking: (params = {}) => api.get('/contributions/ranking/', { params })
}

export default api
