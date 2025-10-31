import axiosClient from "./axiosClient.js";

export const listInvoices = async () => {
  const { data } = await axiosClient.get("/finance/invoices");
  return data;
};

export const markInvoicePaid = async (invoiceId) => {
  const { data } = await axiosClient.post(`/finance/invoices/${invoiceId}/mark-paid`);
  return data;
};
