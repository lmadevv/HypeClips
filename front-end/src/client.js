import axios from "axios"

const instance = axios.create({
  baseURL: "http://localhost:5000/"
})

const request = async (method, url, data) => {
  const headers = {
    authorization: ""
  }

  const res = await instance({
    method,
    url,
    data,
    headers
  })

  return res
}

const get = async (url, data = {}) => request("get", url, data)

const del = async (url, data = {}) => request("delete", url, data)

const post = async (url, data = {}) => request("post", url, data)

const put = async (url, data = {}) => request("put", url, data)

const patch = async (url, data = {}) => request("patch", url, data)

const Client = {
  get,
  del,
  post,
  put,
  patch,
}
export default Client