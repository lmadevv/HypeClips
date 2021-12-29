export default function formatDateString(dateString) {
  // Treat the date string as UTC.
  dateString += ` GMT+00:00`

  const date = new Date(dateString)
  const minute = date.getMinutes() <= 9 ? `0${date.getMinutes()}` : date.getMinutes()
  const time =
    date.getHours() >= 13
      ? `${date.getHours() - 12}:${minute} PM`
      : `${date.getHours()}:${minute} AM`
  return `${date.toDateString().substring(4)}, ${time}`
}