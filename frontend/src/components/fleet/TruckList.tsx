/**
 * Truck list component with filtering and actions.
 */

'use client';

import React, { useState, useMemo } from 'react';
import { Search, MapPin, Fuel, Package, Clock } from 'lucide-react';
import { Truck, TruckStatus } from '@/types';
import { formatDistance, formatPercentage, formatRelativeTime } from '@/lib/utils';
import { Card, DataTable, StatusBadge, Button } from '@/components/ui';
import { TableColumn } from '@/types';

interface TruckListProps {
  trucks: Truck[];
  loading?: boolean;
  error?: string;
  onTruckSelect?: (truck: Truck) => void;
  onTruckUpdate?: (truckId: string, updates: Partial<Truck>) => void;
  className?: string;
}

const TruckList: React.FC<TruckListProps> = ({
  trucks,
  loading = false,
  error,
  onTruckSelect,
  onTruckUpdate,
  className,
}) => {
  const [statusFilter, setStatusFilter] = useState<TruckStatus | 'all'>('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Filter trucks based on status and search term
  const filteredTrucks = useMemo(() => {
    return trucks.filter(truck => {
      const matchesStatus = statusFilter === 'all' || truck.status === statusFilter;
      const matchesSearch = truck.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           truck.id.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesStatus && matchesSearch;
    });
  }, [trucks, statusFilter, searchTerm]);

  // Table columns configuration
  const columns: TableColumn<Truck>[] = [
    {
      key: 'name',
      title: 'Truck',
      sortable: true,
      render: (_, truck) => (
        <div className="flex items-center space-x-3">
          <div className="flex-shrink-0">
            <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
              <span className="text-primary-600 text-sm">🚛</span>
            </div>
          </div>
          <div>
            <div className="font-medium text-gray-900">{truck.name}</div>
            <div className="text-sm text-gray-500">{truck.id}</div>
          </div>
        </div>
      ),
    },
    {
      key: 'status',
      title: 'Status',
      sortable: true,
      render: (_, truck) => <StatusBadge status={truck.status} />,
    },
    {
      key: 'current_location',
      title: 'Location',
      render: (_, truck) => (
        <div className="flex items-center space-x-1">
          <MapPin className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-600">
            {truck.current_location 
              ? `${truck.current_location.latitude.toFixed(4)}, ${truck.current_location.longitude.toFixed(4)}`
              : 'Unknown'
            }
          </span>
        </div>
      ),
    },
    {
      key: 'fuel_level_percent',
      title: 'Fuel',
      sortable: true,
      render: (_, truck) => (
        <div className="flex items-center space-x-2">
          <Fuel className="w-4 h-4 text-gray-400" />
          <div className="flex-1">
            <div className="flex items-center justify-between text-sm">
              <span>{formatPercentage(truck.fuel_level_percent)}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
              <div
                className={`h-2 rounded-full ${
                  truck.fuel_level_percent > 50 
                    ? 'bg-success-500' 
                    : truck.fuel_level_percent > 25 
                    ? 'bg-warning-500' 
                    : 'bg-danger-500'
                }`}
                style={{ width: `${truck.fuel_level_percent}%` }}
              ></div>
            </div>
          </div>
        </div>
      ),
    },
    {
      key: 'current_load_id',
      title: 'Load',
      render: (_, truck) => (
        <div className="flex items-center space-x-1">
          <Package className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-600">
            {truck.current_load_id || 'None'}
          </span>
        </div>
      ),
    },
    {
      key: 'total_distance_km',
      title: 'Distance',
      sortable: true,
      render: (_, truck) => (
        <span className="text-sm text-gray-900">
          {formatDistance(truck.total_distance_km)}
        </span>
      ),
    },
    {
      key: 'last_gps_reading',
      title: 'Last Update',
      sortable: true,
      render: (_, truck) => (
        <div className="flex items-center space-x-1">
          <Clock className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-600">
            {truck.last_gps_reading 
              ? formatRelativeTime(truck.last_gps_reading.timestamp)
              : 'Never'
            }
          </span>
        </div>
      ),
    },
  ];

  // Table actions
  const actions = [
    {
      key: 'view',
      label: 'View',
      icon: MapPin,
      onClick: (truck: Truck) => onTruckSelect?.(truck),
    },
  ];

  // Status filter options
  const statusOptions = [
    { value: 'all', label: 'All Status', count: trucks.length },
    ...Object.values(TruckStatus).map(status => ({
      value: status,
      label: status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
      count: trucks.filter(t => t.status === status).length,
    })),
  ];

  return (
    <div className={className}>
      <Card>
        <Card.Header 
          title="Fleet Overview"
          subtitle={`${filteredTrucks.length} of ${trucks.length} trucks`}
        />
        
        <Card.Content>
          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search trucks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            {/* Status Filter */}
            <div className="flex flex-wrap gap-2">
              {statusOptions.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setStatusFilter(option.value as TruckStatus | 'all')}
                  className={`px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                    statusFilter === option.value
                      ? 'bg-primary-100 text-primary-700 border border-primary-200'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-200'
                  }`}
                >
                  {option.label}
                  <span className="ml-1 text-xs opacity-75">({option.count})</span>
                </button>
              ))}
            </div>
          </div>

          {/* Truck Table */}
          <DataTable
            data={filteredTrucks}
            columns={columns}
            loading={loading}
            error={error}
            actions={actions}
            pagination={{
              current: 1,
              pageSize: 10,
              total: filteredTrucks.length,
              onChange: () => {}, // Implement pagination if needed
            }}
          />
        </Card.Content>
      </Card>
    </div>
  );
};

export default TruckList;