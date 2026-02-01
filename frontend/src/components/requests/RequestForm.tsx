'use client';

import { useState } from 'react';
import { Package, MapPin, Clock, User, AlertTriangle, Thermometer } from 'lucide-react';
import { Button, LoadingSpinner } from '@/components/ui';
import { createRequest } from '@/lib/api';

interface RequestFormProps {
  onSuccess: () => void;
  onCancel: () => void;
}

interface FormData {
  customer_name: string;
  customer_phone: string;
  customer_email: string;
  description: string;
  weight_kg: number;
  volume_m3: number;
  priority: string;
  pickup_address: string;
  delivery_address: string;
  preferred_pickup_time: string;
  delivery_deadline: string;
  special_instructions: string;
  fragile: boolean;
  temperature_controlled: boolean;
}

export function RequestForm({ onSuccess, onCancel }: RequestFormProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<FormData>({
    customer_name: '',
    customer_phone: '',
    customer_email: '',
    description: '',
    weight_kg: 0,
    volume_m3: 0,
    priority: 'normal',
    pickup_address: '',
    delivery_address: '',
    preferred_pickup_time: '',
    delivery_deadline: '',
    special_instructions: '',
    fragile: false,
    temperature_controlled: false,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Prepare data for API
      const requestData = {
        ...formData,
        weight_kg: Number(formData.weight_kg),
        volume_m3: formData.volume_m3 ? Number(formData.volume_m3) : null,
        preferred_pickup_time: formData.preferred_pickup_time || null,
        delivery_deadline: formData.delivery_deadline || null,
      };

      await createRequest(requestData);
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create request');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: keyof FormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Customer Information */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 text-lg font-semibold text-gray-900">
          <User className="h-5 w-5" />
          <span>Customer Information</span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Customer Name *
            </label>
            <input
              type="text"
              required
              value={formData.customer_name}
              onChange={(e) => handleChange('customer_name', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="John Doe"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Phone Number
            </label>
            <input
              type="tel"
              value={formData.customer_phone}
              onChange={(e) => handleChange('customer_phone', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="+1 (555) 123-4567"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email Address
          </label>
          <input
            type="email"
            value={formData.customer_email}
            onChange={(e) => handleChange('customer_email', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="john@example.com"
          />
        </div>
      </div>

      {/* Package Information */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 text-lg font-semibold text-gray-900">
          <Package className="h-5 w-5" />
          <span>Package Information</span>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description *
          </label>
          <input
            type="text"
            required
            value={formData.description}
            onChange={(e) => handleChange('description', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Electronics, furniture, documents, etc."
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Weight (kg) *
            </label>
            <input
              type="number"
              required
              min="0.1"
              step="0.1"
              value={formData.weight_kg || ''}
              onChange={(e) => handleChange('weight_kg', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="10.5"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Volume (m³)
            </label>
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={formData.volume_m3 || ''}
              onChange={(e) => handleChange('volume_m3', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="0.5"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Priority
            </label>
            <select
              value={formData.priority}
              onChange={(e) => handleChange('priority', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="low">Low</option>
              <option value="normal">Normal</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </div>

        {/* Special Requirements */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Special Requirements
          </label>
          <div className="flex space-x-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.fragile}
                onChange={(e) => handleChange('fragile', e.target.checked)}
                className="mr-2"
              />
              <AlertTriangle className="h-4 w-4 mr-1 text-orange-500" />
              <span className="text-sm">Fragile</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.temperature_controlled}
                onChange={(e) => handleChange('temperature_controlled', e.target.checked)}
                className="mr-2"
              />
              <Thermometer className="h-4 w-4 mr-1 text-blue-500" />
              <span className="text-sm">Temperature Controlled</span>
            </label>
          </div>
        </div>
      </div>

      {/* Location Information */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 text-lg font-semibold text-gray-900">
          <MapPin className="h-5 w-5" />
          <span>Locations</span>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Pickup Address *
          </label>
          <input
            type="text"
            required
            value={formData.pickup_address}
            onChange={(e) => handleChange('pickup_address', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="123 Main St, New York, NY 10001"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Delivery Address *
          </label>
          <input
            type="text"
            required
            value={formData.delivery_address}
            onChange={(e) => handleChange('delivery_address', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="456 Oak Ave, Brooklyn, NY 11201"
          />
        </div>
      </div>

      {/* Timing */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 text-lg font-semibold text-gray-900">
          <Clock className="h-5 w-5" />
          <span>Timing Preferences</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Preferred Pickup Time
            </label>
            <input
              type="datetime-local"
              value={formData.preferred_pickup_time}
              onChange={(e) => handleChange('preferred_pickup_time', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Delivery Deadline
            </label>
            <input
              type="datetime-local"
              value={formData.delivery_deadline}
              onChange={(e) => handleChange('delivery_deadline', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </div>

      {/* Special Instructions */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Special Instructions
        </label>
        <textarea
          value={formData.special_instructions}
          onChange={(e) => handleChange('special_instructions', e.target.value)}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder="Any special handling instructions, access codes, etc."
        />
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-md">
          <div className="flex items-center text-red-700">
            <AlertTriangle className="h-4 w-4 mr-2" />
            <span className="text-sm">{error}</span>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-end space-x-3 pt-4 border-t">
        <Button
          type="button"
          variant="ghost"
          onClick={onCancel}
          disabled={loading}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          disabled={loading}
          className="flex items-center space-x-2"
        >
          {loading && <LoadingSpinner size="sm" />}
          <span>{loading ? 'Creating...' : 'Create Request'}</span>
        </Button>
      </div>
    </form>
  );
}