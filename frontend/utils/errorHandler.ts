export function extractErrorMessage(err: any, defaultMessage: string = 'An error occurred'): string {
  try {
    if (typeof err === 'string') {
      return err
    }

    if (err.response?.data) {
      const { detail, message, msg } = err.response.data

      if (typeof detail === 'string') {
        return detail
      }

      if (Array.isArray(detail)) {
        return detail
          .map((e: any) => {
            if (typeof e === 'string') return e
            if (typeof e === 'object' && e.msg) return e.msg
            return JSON.stringify(e)
          })
          .filter(Boolean)
          .join(', ')
      }

      if (typeof detail === 'object' && detail.msg) {
        return detail.msg
      }

      if (typeof message === 'string') {
        return message
      }

      if (typeof msg === 'string') {
        return msg
      }
    }

    if (err.message && typeof err.message === 'string') {
      return err.message
    }

    return defaultMessage
  } catch {
    return defaultMessage
  }
}
