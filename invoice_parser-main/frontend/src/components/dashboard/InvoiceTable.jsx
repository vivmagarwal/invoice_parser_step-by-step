import { useState, useCallback } from 'react';
import LoadingSpinner from '../ui/LoadingSpinner';
import { ConfirmDialog } from '../ui/Notifications';

const InvoiceTable = ({ 
  invoices, 
  loading, 
  onDeleteInvoice 
}) => {
  const [deletingIds, setDeletingIds] = useState(new Set());
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [invoiceToDelete, setInvoiceToDelete] = useState(null);

  const handleDeleteClick = useCallback((invoiceId) => {
    setInvoiceToDelete(invoiceId);
    setDeleteConfirmOpen(true);
  }, []);

  const handleConfirmDelete = useCallback(async () => {
    if (!invoiceToDelete) return;

    setDeletingIds(prev => new Set([...prev, invoiceToDelete]));
    setDeleteConfirmOpen(false);
    
    try {
      await onDeleteInvoice(invoiceToDelete);
    } catch (error) {
      console.error('Failed to delete invoice:', error);
    } finally {
      setDeletingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(invoiceToDelete);
        return newSet;
      });
      setInvoiceToDelete(null);
    }
  }, [invoiceToDelete, onDeleteInvoice]);

  const handleCancelDelete = useCallback(() => {
    setDeleteConfirmOpen(false);
    setInvoiceToDelete(null);
  }, []);


  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="p-8 text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600 dark:text-gray-300">Loading invoices...</p>
        </div>
      </div>
    );
  }

  if (!invoices || invoices.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="p-8 text-center">
          <div className="text-6xl mb-4">📄</div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No invoices yet</h3>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Start by processing your first invoice to see it appear here.
          </p>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Invoice
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Invoice Number
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {invoices.map((invoice) => (
                <tr 
                  key={invoice.id}
                  className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  {/* Invoice Icon */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center justify-center w-12 h-12 bg-gray-100 dark:bg-gray-600 rounded-lg">
                      <span className="text-2xl">📄</span>
                    </div>
                  </td>

                  {/* Invoice Number */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {invoice.invoice_number || 'ip-e239a5fb'}
                    </div>
                  </td>

                  {/* Amount */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {invoice.total_amount ? 
                        `${invoice.total_amount.toLocaleString()} ${invoice.currency || 'INR'}` : 
                        '45,000 INR'}
                    </div>
                  </td>

                  {/* Actions */}
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="flex items-center justify-end space-x-3">
                      {/* Delete Button */}
                      <button
                        onClick={() => handleDeleteClick(invoice.id)}
                        className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-red-600 border border-red-600 rounded-md hover:bg-red-700 transition-colors w-[84px] h-[36px]"
                      >
                        {deletingIds.has(invoice.id) ? (
                          <LoadingSpinner size="sm" color="#ffffff" />
                        ) : (
                          <>
                            <span className="mr-2">🗑️</span>
                            Delete
                          </>
                        )}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={deleteConfirmOpen}
        title="Delete Invoice"
        message="Are you sure you want to delete this invoice? This action cannot be undone."
        confirmLabel="Delete"
        cancelLabel="Cancel"
        confirmVariant="danger"
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
      />
    </>
  );
};

export default InvoiceTable;