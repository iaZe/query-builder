import axios from 'axios';

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error) && error.response) {
    if (error.response.data && error.response.data.detail) {
      return error.response.data.detail;
    }
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'Ocorreu um erro inesperado.';
}
