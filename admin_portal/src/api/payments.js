import axiosClient from "./axiosClient.js";

export const listInvoices = async () => {
  const { data } = await axiosClient.get("/payments/");
  return data;
};

export const markInvoicePaid = async (invoiceId) => {
  const { data } = await axiosClient.post(`/payments/${invoiceId}/mark-paid`);
  return data;
};
