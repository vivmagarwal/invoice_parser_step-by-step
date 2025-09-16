import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import LoadingSpinner from '../ui/LoadingSpinner';
import { useKeyboardNavigation } from '../../hooks/useKeyboardNavigation';

const InvoicePreviewModal = ({ isOpen, onClose, invoiceId }) => {
  const { apiRequest } = useAuth();
  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const modalRef = useRef(null);

  // Add keyboard navigation for ESC key
  useKeyboardNavigation(isOpen, onClose);

  useEffect(() => {
    if (isOpen && invoiceId) {
      fetchInvoiceDetails();
    }
  }, [isOpen, invoiceId]);

  const fetchInvoiceDetails = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiRequest(`/api/invoices/${invoiceId}`);
      
      if (result.success) {
        setInvoice(result.data);
      } else {
        setError('Failed to load invoice details');
      }
    } catch (err) {
      console.error('Error fetching invoice details:', err);
      setError('Failed to load invoice details');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[9999] overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-4 text-center sm:p-0">
        {/* Backdrop */}
        <div 
          className="modal-overlay"
          onClick={onClose}
        ></div>

        {/* Modal content */}
        <div 
          ref={modalRef}
          className="inline-block align-middle bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto text-left transform transition-all"
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
          tabIndex="-1"
          onClick={(e) => e.stopPropagation()}
        >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">📄</span>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
              Invoice Details
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 p-2"
          >
            <span className="text-xl">✕</span>
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <LoadingSpinner size="lg" />
              <span className="ml-3 text-gray-600 dark:text-gray-400">Loading invoice details...</span>
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <div className="text-red-600 dark:text-red-400 mb-2">
                <div className="text-4xl mx-auto mb-2 opacity-50">📄</div>
                <p className="text-lg font-semibold">Error Loading Invoice</p>
                <p className="text-sm">{error}</p>
              </div>
              <button
                onClick={fetchInvoiceDetails}
                className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Retry
              </button>
            </div>
          ) : invoice ? (
            <div className="space-y-6">
              {/* Basic Invoice Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <span className="text-indigo-600">📄</span>
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Invoice Number</p>
                      <p className="font-semibold text-gray-900 dark:text-gray-100">
                        {invoice.invoice_number || 'N/A'}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <span className="text-indigo-600">📅</span>
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Invoice Date</p>
                      <p className="font-semibold text-gray-900 dark:text-gray-100">
                        {invoice.invoice_date ? new Date(invoice.invoice_date).toLocaleDateString() : 'N/A'}
                      </p>
                    </div>
                  </div>

                  {invoice.due_date && (
                    <div className="flex items-center space-x-3">
                      <span className="text-indigo-600">⏰</span>
                      <div>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Due Date</p>
                        <p className="font-semibold text-gray-900 dark:text-gray-100">
                          {new Date(invoice.due_date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <span className="text-indigo-600">💰</span>
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Total Amount</p>
                      <p className="font-semibold text-gray-900 dark:text-gray-100 text-lg">
                        {invoice.currency} {invoice.total_amount?.toLocaleString() || '0.00'}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <span className="text-indigo-600">💵</span>
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Net Amount</p>
                      <p className="font-semibold text-gray-900 dark:text-gray-100">
                        {invoice.currency} {invoice.net_amount?.toLocaleString() || '0.00'}
                      </p>
                    </div>
                  </div>

                  {invoice.gross_amount && (
                    <div className="flex items-center space-x-3">
                      <span className="text-indigo-600">💳</span>
                      <div>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Gross Amount</p>
                        <p className="font-semibold text-gray-900 dark:text-gray-100">
                          {invoice.currency} {invoice.gross_amount?.toLocaleString() || '0.00'}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Vendor Information */}
              {invoice.vendor && (
                <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
                    <span className="text-indigo-600 mr-2">🏢</span>
                    Vendor Information
                  </h3>
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Company Name</p>
                        <p className="font-semibold text-gray-900 dark:text-gray-100">
                          {invoice.vendor.company_name || 'N/A'}
                        </p>
                      </div>
                      {invoice.vendor.gstin && (
                        <div>
                          <p className="text-sm text-gray-500 dark:text-gray-400">GSTIN</p>
                          <p className="font-semibold text-gray-900 dark:text-gray-100">
                            {invoice.vendor.gstin}
                          </p>
                        </div>
                      )}
                      {invoice.vendor.phone && (
                        <div>
                          <p className="text-sm text-gray-500 dark:text-gray-400">Phone</p>
                          <p className="font-semibold text-gray-900 dark:text-gray-100">
                            {invoice.vendor.phone}
                          </p>
                        </div>
                      )}
                      {invoice.vendor.email && (
                        <div>
                          <p className="text-sm text-gray-500 dark:text-gray-400">Email</p>
                          <p className="font-semibold text-gray-900 dark:text-gray-100">
                            {invoice.vendor.email}
                          </p>
                        </div>
                      )}
                    </div>
                    {invoice.vendor.addresses && invoice.vendor.addresses.length > 0 && (
                      <div className="mt-4">
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Address</p>
                        {invoice.vendor.addresses.map((addr, index) => (
                          <div key={index} className="text-sm text-gray-900 dark:text-gray-100">
                            <p>{addr.street}</p>
                            <p>{addr.city}, {addr.state} {addr.pincode}</p>
                            <p>{addr.country}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Customer Information */}
              {invoice.customer && (
                <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
                    <span className="text-indigo-600 mr-2">👤</span>
                    Customer Information
                  </h3>
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Company Name</p>
                        <p className="font-semibold text-gray-900 dark:text-gray-100">
                          {invoice.customer.company_name || 'N/A'}
                        </p>
                      </div>
                      {invoice.customer.gstin && (
                        <div>
                          <p className="text-sm text-gray-500 dark:text-gray-400">GSTIN</p>
                          <p className="font-semibold text-gray-900 dark:text-gray-100">
                            {invoice.customer.gstin}
                          </p>
                        </div>
                      )}
                      {invoice.customer.phone && (
                        <div>
                          <p className="text-sm text-gray-500 dark:text-gray-400">Phone</p>
                          <p className="font-semibold text-gray-900 dark:text-gray-100">
                            {invoice.customer.phone}
                          </p>
                        </div>
                      )}
                      {invoice.customer.email && (
                        <div>
                          <p className="text-sm text-gray-500 dark:text-gray-400">Email</p>
                          <p className="font-semibold text-gray-900 dark:text-gray-100">
                            {invoice.customer.email}
                          </p>
                        </div>
                      )}
                    </div>
                    {invoice.customer.addresses && invoice.customer.addresses.length > 0 && (
                      <div className="mt-4">
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Address</p>
                        {invoice.customer.addresses.map((addr, index) => (
                          <div key={index} className="text-sm text-gray-900 dark:text-gray-100">
                            <p>{addr.street}</p>
                            <p>{addr.city}, {addr.state} {addr.pincode}</p>
                            <p>{addr.country}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Line Items */}
              {invoice.line_items && invoice.line_items.length > 0 && (
                <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
                    <span className="text-indigo-600 mr-2">📋</span>
                    Line Items
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-600">
                      <thead className="bg-gray-50 dark:bg-gray-700">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            S.No
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            Description
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            HSN
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            Qty
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            Rate
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            Amount
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-600">
                        {invoice.line_items.map((item, index) => (
                          <tr key={item.id || index}>
                            <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                              {item.serial_number || index + 1}
                            </td>
                            <td className="px-4 py-4 text-sm text-gray-900 dark:text-gray-100">
                              {item.description || 'N/A'}
                            </td>
                            <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                              {item.hsn_code || 'N/A'}
                            </td>
                            <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                              {item.quantity || 0} {item.unit || ''}
                            </td>
                            <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                              {invoice.currency} {item.rate?.toLocaleString() || '0.00'}
                            </td>
                            <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                              {invoice.currency} {item.amount?.toLocaleString() || '0.00'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Tax Calculations */}
              {invoice.tax_calculation && (
                <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
                    <span className="text-indigo-600 mr-2">🧾</span>
                    Tax Calculations
                  </h3>
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Taxable Amount</p>
                        <p className="font-semibold text-gray-900 dark:text-gray-100">
                          {invoice.currency} {invoice.tax_calculation.taxable_amount?.toLocaleString() || '0.00'}
                        </p>
                      </div>
                      {invoice.tax_calculation.cgst_rate && (
                        <>
                          <div>
                            <p className="text-sm text-gray-500 dark:text-gray-400">CGST ({invoice.tax_calculation.cgst_rate}%)</p>
                            <p className="font-semibold text-gray-900 dark:text-gray-100">
                              {invoice.currency} {invoice.tax_calculation.cgst_amount?.toLocaleString() || '0.00'}
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-500 dark:text-gray-400">SGST ({invoice.tax_calculation.sgst_rate}%)</p>
                            <p className="font-semibold text-gray-900 dark:text-gray-100">
                              {invoice.currency} {invoice.tax_calculation.sgst_amount?.toLocaleString() || '0.00'}
                            </p>
                          </div>
                        </>
                      )}
                      {invoice.tax_calculation.igst_rate && (
                        <div>
                          <p className="text-sm text-gray-500 dark:text-gray-400">IGST ({invoice.tax_calculation.igst_rate}%)</p>
                          <p className="font-semibold text-gray-900 dark:text-gray-100">
                            {invoice.currency} {invoice.tax_calculation.igst_amount?.toLocaleString() || '0.00'}
                          </p>
                        </div>
                      )}
                      <div>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Total Tax</p>
                        <p className="font-semibold text-gray-900 dark:text-gray-100 text-lg">
                          {invoice.currency} {invoice.tax_calculation.total_tax?.toLocaleString() || '0.00'}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Amount in Words */}
              {invoice.amount_in_words && (
                <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
                    <span className="text-indigo-600 mr-2">💬</span>
                    Amount in Words
                  </h3>
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <p className="text-gray-900 dark:text-gray-100 italic">
                      {invoice.amount_in_words}
                    </p>
                  </div>
                </div>
              )}

              {/* Additional Details */}
              {invoice.extracted_data && (
                <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                    Extracted Data
                  </h3>
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <pre className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
                      {JSON.stringify(invoice.extracted_data, null, 2)}
                    </pre>
                  </div>
                </div>
              )}

              {/* Original Image Preview */}
              {invoice.original_file_id && (
                <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                    Original Document
                  </h3>
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <img
                      src={`/api/files/${invoice.original_file_id}/preview`}
                      alt="Invoice Preview"
                      className="max-w-full h-auto rounded-lg border border-gray-300 dark:border-gray-600"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'block';
                      }}
                    />
                    <div 
                      className="text-center py-8 text-gray-500 dark:text-gray-400 hidden"
                    >
                      <div className="text-4xl mx-auto mb-2 opacity-50">📄</div>
                      <p>Preview not available</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-4xl text-gray-400 mx-auto mb-2 opacity-50">📄</div>
              <p className="text-gray-500 dark:text-gray-400">No invoice data available</p>
            </div>
          )}
        </div>

          {/* Footer */}
          <div className="flex justify-end px-6 py-4 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InvoicePreviewModal;
