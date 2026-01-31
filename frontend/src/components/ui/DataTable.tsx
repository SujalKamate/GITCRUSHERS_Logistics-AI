/**
 * Data table component with sorting, filtering, and pagination.
 */

'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { ChevronUp, ChevronDown, Search } from 'lucide-react';
import { DataTableProps, TableColumn } from '@/types';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import Button from './Button';

function DataTable<T extends Record<string, any>>({
  data,
  columns,
  loading = false,
  error,
  pagination,
  sorting,
  filtering,
  selection,
  actions,
  className,
}: DataTableProps<T>) {
  const [searchTerm, setSearchTerm] = useState('');

  // Filter data based on search term
  const filteredData = React.useMemo(() => {
    if (!searchTerm) return data;
    
    return data.filter(item =>
      columns.some(column => {
        const value = item[column.key as keyof T];
        return String(value).toLowerCase().includes(searchTerm.toLowerCase());
      })
    );
  }, [data, columns, searchTerm]);

  const handleSort = (field: string) => {
    if (!sorting) return;
    
    const newOrder = sorting.field === field && sorting.order === 'asc' ? 'desc' : 'asc';
    sorting.onChange(field, newOrder);
  };

  const renderSortIcon = (column: TableColumn<T>) => {
    if (!column.sortable || !sorting) return null;
    
    const isActive = sorting.field === column.key;
    const isAsc = sorting.order === 'asc';
    
    return (
      <span className="ml-1 inline-flex flex-col">
        <ChevronUp 
          className={cn(
            'w-3 h-3 -mb-1',
            isActive && isAsc ? 'text-primary-600' : 'text-gray-400'
          )} 
        />
        <ChevronDown 
          className={cn(
            'w-3 h-3',
            isActive && !isAsc ? 'text-primary-600' : 'text-gray-400'
          )} 
        />
      </span>
    );
  };

  const renderCell = (item: T, column: TableColumn<T>, index: number) => {
    const value = item[column.key as keyof T];
    
    if (column.render) {
      return column.render(value, item, index);
    }
    
    return String(value || '');
  };

  if (loading) {
    return (
      <div className="p-8">
        <LoadingSpinner size="lg" text="Loading data..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <ErrorMessage error={error} />
      </div>
    );
  }

  return (
    <div className={cn('bg-white rounded-lg border border-gray-200', className)}>
      {/* Search and filters */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          
          {actions && actions.length > 0 && (
            <div className="flex space-x-2">
              {actions.map((action) => (
                <Button
                  key={action.key}
                  variant="outline"
                  size="sm"
                  icon={action.icon && <action.icon className="w-4 h-4" />}
                  onClick={() => {
                    // Handle bulk actions here if needed
                  }}
                >
                  {action.label}
                </Button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              {selection && (
                <th className="px-4 py-3 text-left">
                  <input
                    type="checkbox"
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    onChange={(e) => {
                      const allKeys = filteredData.map((_, index) => String(index));
                      selection.onChange(
                        e.target.checked ? allKeys : [],
                        e.target.checked ? filteredData : []
                      );
                    }}
                  />
                </th>
              )}
              
              {columns.map((column) => (
                <th
                  key={String(column.key)}
                  className={cn(
                    'px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
                    column.sortable && 'cursor-pointer hover:bg-gray-100',
                    column.align === 'center' && 'text-center',
                    column.align === 'right' && 'text-right'
                  )}
                  style={{ width: column.width }}
                  onClick={() => column.sortable && handleSort(String(column.key))}
                >
                  <div className="flex items-center">
                    {column.title}
                    {renderSortIcon(column)}
                  </div>
                </th>
              ))}
              
              {actions && actions.length > 0 && (
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              )}
            </tr>
          </thead>
          
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredData.map((item, index) => (
              <tr key={index} className="hover:bg-gray-50">
                {selection && (
                  <td className="px-4 py-4">
                    <input
                      type="checkbox"
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      checked={selection.selectedRowKeys.includes(String(index))}
                      onChange={(e) => {
                        const newSelection = e.target.checked
                          ? [...selection.selectedRowKeys, String(index)]
                          : selection.selectedRowKeys.filter(key => key !== String(index));
                        
                        const selectedItems = newSelection.map(key => filteredData[parseInt(key)]);
                        selection.onChange(newSelection, selectedItems);
                      }}
                    />
                  </td>
                )}
                
                {columns.map((column) => (
                  <td
                    key={String(column.key)}
                    className={cn(
                      'px-4 py-4 text-sm text-gray-900',
                      column.align === 'center' && 'text-center',
                      column.align === 'right' && 'text-right'
                    )}
                  >
                    {renderCell(item, column, index)}
                  </td>
                ))}
                
                {actions && actions.length > 0 && (
                  <td className="px-4 py-4 text-right text-sm">
                    <div className="flex items-center justify-end space-x-2">
                      {actions.map((action) => (
                        <Button
                          key={action.key}
                          variant={action.danger ? 'danger' : 'ghost'}
                          size="sm"
                          disabled={action.disabled?.(item)}
                          onClick={() => action.onClick(item)}
                          icon={action.icon && <action.icon className="w-4 h-4" />}
                        >
                          {action.label}
                        </Button>
                      ))}
                    </div>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && (
        <div className="px-4 py-3 border-t border-gray-200 flex items-center justify-between">
          <div className="text-sm text-gray-700">
            Showing {Math.min((pagination.current - 1) * pagination.pageSize + 1, pagination.total)} to{' '}
            {Math.min(pagination.current * pagination.pageSize, pagination.total)} of{' '}
            {pagination.total} results
          </div>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              disabled={pagination.current === 1}
              onClick={() => pagination.onChange(pagination.current - 1, pagination.pageSize)}
            >
              Previous
            </Button>
            
            <span className="text-sm text-gray-700">
              Page {pagination.current} of {Math.ceil(pagination.total / pagination.pageSize)}
            </span>
            
            <Button
              variant="outline"
              size="sm"
              disabled={pagination.current >= Math.ceil(pagination.total / pagination.pageSize)}
              onClick={() => pagination.onChange(pagination.current + 1, pagination.pageSize)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export default DataTable;