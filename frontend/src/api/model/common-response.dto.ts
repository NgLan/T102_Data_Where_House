/** Success envelope legacy cho operation chưa có trong generated SDK. */
export interface ApiResponse<T> {
  status: 'success';
  code: number;
  message: string;
  data: T;
}
