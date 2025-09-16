// Simple icon components using Unicode symbols and CSS
import React from 'react';

const iconStyles = {
  base: {
    display: 'inline-block',
    fontSize: '1em',
    lineHeight: 1,
    textAlign: 'center',
    verticalAlign: 'middle',
  }
};

// Simple icon components
export const DocumentTextIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>📄</span>
);

export const DocumentCheckIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>📋✅</span>
);

export const CheckCircleIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>✅</span>
);

export const XCircleIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>❌</span>
);

export const InformationCircleIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>ℹ️</span>
);

export const ExclamationTriangleIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>⚠️</span>
);

export const XMarkIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>✕</span>
);

export const ArrowPathIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>🔄</span>
);

export const CloudUploadIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>☁️⬆️</span>
);

export const PhotoIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>🖼️</span>
);

export const ClockIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>🕐</span>
);

export const ChartBarIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>📊</span>
);

export const ArrowUpIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>⬆️</span>
);

export const ArrowDownIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>⬇️</span>
);

export const ArrowRightIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>➡️</span>
);

export const CogIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>⚙️</span>
);

export const UserIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>👤</span>
);

export const ChevronDownIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>⌄</span>
);

export const ChevronLeftIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>‹</span>
);

export const ChevronRightIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>›</span>
);

export const Bars3Icon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>☰</span>
);

export const PlusIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>+</span>
);

export const CpuChipIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>🔧</span>
);

export const ShieldCheckIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>🛡️</span>
);

export const BoltIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>⚡</span>
);

export const PlayIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>▶️</span>
);

export const ClipboardIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>📋</span>
);

export const EyeIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>👁️</span>
);

export const TrashIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>🗑️</span>
);

export const CalendarIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>📅</span>
);

export const BuildingOfficeIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>🏢</span>
);

export const CurrencyDollarIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>💰</span>
);

export const ArchiveBoxIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>📦</span>
);

export const MagnifyingGlassIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>🔍</span>
);

export const FunnelIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>🔽</span>
);

export const FileIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>📁</span>
);

export const PencilIcon = ({ className = '', style = {} }) => (
  <span className={className} style={{...iconStyles.base, ...style}}>✏️</span>
);

export default {
  DocumentTextIcon,
  DocumentCheckIcon,
  CheckCircleIcon,
  XCircleIcon,
  InformationCircleIcon,
  ExclamationTriangleIcon,
  XMarkIcon,
  ArrowPathIcon,
  CloudUploadIcon,
  PhotoIcon,
  ClockIcon,
  ChartBarIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  ArrowRightIcon,
  CogIcon,
  UserIcon,
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  Bars3Icon,
  PlusIcon,
  CpuChipIcon,
  ShieldCheckIcon,
  BoltIcon,
  PlayIcon,
  ClipboardIcon,
  EyeIcon,
  TrashIcon,
  CalendarIcon,
  BuildingOfficeIcon,
  CurrencyDollarIcon,
  ArchiveBoxIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  FileIcon,
  PencilIcon
};