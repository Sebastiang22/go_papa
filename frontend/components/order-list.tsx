"use client"

import { useState } from "react"
import {
  type ColumnDef,
  type ColumnFiltersState,
  type SortingState,
  type VisibilityState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table"
import { ArrowUpDown, ChevronDown, Filter, Search, Loader2, CheckCircle, Clock, Trash2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { StatusBadge } from "@/components/status-badge"

export type Product = {
  name: string
  quantity: number
  price: number
  observations?: string // Campo opcional para observaciones
}

export type Order = {
  table_id: string
  customer_name: string
  products: Product[]
  created_at: string
  updated_at: string
  state: string
  id: string
}

// Función para formatear la fecha
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat("es-ES", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date)
}

// Función para formatear números a pesos colombianos
const formatCOP = (value: number) => {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

interface OrderListProps {
  orders: Order[]
  onSelectOrder: (order: Order) => void
  onStatusUpdate: (orderId: string, newStatus: string) => void
  onDeleteOrder: (orderId: string) => void
  updatingOrderIds?: Set<string>
  setUpdatingOrderIds?: (updater: (prev: Set<string>) => Set<string>) => void
}

export function OrderList({ orders, onSelectOrder, onStatusUpdate, onDeleteOrder, updatingOrderIds = new Set(), setUpdatingOrderIds }: OrderListProps) {
  const [sorting, setSorting] = useState<SortingState>([
    { id: "created_at", desc: true }
  ])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({})
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<string | null>(null)

  // Función para manejar el cambio en el filtro de estado
  const handleStatusFilterChange = (status: string | null) => {
    setStatusFilter(status)
    
    if (status) {
      // Aplicar filtro por estado
      setColumnFilters(prev => {
        // Eliminar filtro anterior de estado si existe
        const filteredValues = prev.filter(filter => filter.id !== "state")
        // Añadir nuevo filtro
        return [...filteredValues, { id: "state", value: status }]
      })
    } else {
      // Eliminar filtro por estado
      setColumnFilters(prev => prev.filter(filter => filter.id !== "state"))
    }
  }

  const handleStatusUpdate = async (orderId: string, newStatus: string) => {
    // Si se proporciona setUpdatingOrderIds, usarlo, de lo contrario no hacer nada con updatingOrderIds
    setUpdatingOrderIds?.(prev => new Set(prev).add(orderId));
    
    try {
      await onStatusUpdate(orderId, newStatus);
    } finally {
      setUpdatingOrderIds?.(prev => {
        const newSet = new Set(prev);
        newSet.delete(orderId);
        return newSet;
      });
    }
  }

  const columns: ColumnDef<Order>[] = [
    {
      accessorKey: "id",
      header: "# Pedido",
      cell: ({ row }) => <span className="font-medium">#{row.getValue("id")}</span>,
    },
    {
      accessorKey: "table_id",
      header: "Dirección",
      cell: ({ row }) => <div className="max-w-[200px] truncate">{row.getValue("table_id")}</div>,
    },
    {
      accessorKey: "customer_name",
      header: ({ column }) => {
        return (
          <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
            Cliente
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
    },
    {
      accessorKey: "products",
      header: "Productos",
      cell: ({ row }) => {
        const products = row.getValue("products") as Product[]
        const totalItems = products.reduce((sum, product) => sum + product.quantity, 0)
        return <div>{totalItems} item(s)</div>
      },
    },
    {
      id: "total_price",
      header: "Total",
      cell: ({ row }) => {
        const products = row.getValue("products") as Product[]
        const totalPrice = products.reduce((sum, product) => sum + (product.price * product.quantity), 0)
        return <div className="font-medium">{formatCOP(totalPrice)}</div>
      },
    },
    {
      accessorKey: "created_at",
      header: ({ column }) => (
        <div className="flex items-center">
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="p-0 hover:bg-transparent"
          >
            Fecha
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        </div>
      ),
      cell: ({ row }) => {
        return <div className="font-medium">{formatDate(row.getValue("created_at"))}</div>
      },
      sortingFn: (rowA, rowB, columnId) => {
        const dateA = new Date(rowA.getValue(columnId)).getTime()
        const dateB = new Date(rowB.getValue(columnId)).getTime()
        return dateA < dateB ? -1 : dateA > dateB ? 1 : 0
      },
    },
    {
      accessorKey: "state",
      header: ({ column }) => (
        <div className="flex items-center">
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="p-0 hover:bg-transparent"
          >
            Estado
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
          {/* Añadir menú de filtro por estado */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="ml-1 h-8 w-8">
                <Filter className="h-4 w-4" />
                {statusFilter && <span className="absolute -right-1 -top-1 h-2 w-2 rounded-full bg-primary" />}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem 
                onClick={() => handleStatusFilterChange(null)}
                className={!statusFilter ? "bg-accent/50" : ""}
              >
                Todos
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem 
                onClick={() => handleStatusFilterChange("pendiente")}
                className={statusFilter === "pendiente" ? "bg-accent/50" : ""}
              >
                Pendientes
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={() => handleStatusFilterChange("en preparación")}
                className={statusFilter === "en preparación" ? "bg-accent/50" : ""}
              >
                En preparación
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={() => handleStatusFilterChange("completado")}
                className={statusFilter === "completado" ? "bg-accent/50" : ""}
              >
                Completados
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      ),
      cell: ({ row }) => {
        const status = row.getValue("state") as string
        
        if (updatingOrderIds.has(row.original.id)) {
          return (
            <div className="flex items-center">
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              <StatusBadge status={status} />
            </div>
          )
        }
        
        return <StatusBadge status={status} />
      },
      filterFn: (row, id, value) => {
        return row.getValue(id) === value
      },
    },
    {
      id: "actions",
      header: "Acciones",
      cell: ({ row }) => {
        const order = row.original
        const isUpdating = updatingOrderIds.has(order.id)
        
        return (
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                onDeleteOrder(order.id)
              }}
              disabled={isUpdating}
              className="text-red-500 hover:text-red-700 hover:bg-red-50"
            >
              {isUpdating ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Trash2 className="h-4 w-4" />
              )}
              <span className="sr-only">Eliminar</span>
            </Button>
          </div>
        )
      },
    },
  ]

  // Filtrar órdenes basado en el término de búsqueda global
  const filteredOrders = searchTerm
    ? orders.filter(
        (order) =>
          order.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          order.products.some(
            (product) =>
              product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
              (product.observations && product.observations.toLowerCase().includes(searchTerm.toLowerCase())),
          ),
      )
    : orders

  const table = useReactTable({
    data: filteredOrders,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onColumnVisibilityChange: setColumnVisibility,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      globalFilter: searchTerm,
    },
    initialState: {
      pagination: {
        pageSize: 10,
      },
    },
    enableGlobalFilter: true,
    globalFilterFn: (row, id, filterValue) => {
      const safeValue = (value: unknown): string => {
        if (typeof value === 'string') return value.toLowerCase()
        if (typeof value === 'number') return value.toString()
        if (value === null || value === undefined) return ''
        if (typeof value === 'object') {
          // Manejar caso específico de products
          if (Array.isArray(value) && id === 'products') {
            return value.map(product => product.name).join(' ').toLowerCase()
          }
          return JSON.stringify(value).toLowerCase()
        }
        return String(value).toLowerCase()
      }
      
      const searchValue = filterValue.toLowerCase()
      const customerName = safeValue(row.getValue('customer_name'))
      const tableId = safeValue(row.getValue('table_id'))
      const products = row.getValue('products') as Product[]
      const productsText = products
        .map(p => `${p.name} ${p.observations || ''}`)
        .join(' ')
        .toLowerCase()
      
      return customerName.includes(searchValue) || 
             tableId.includes(searchValue) || 
             productsText.includes(searchValue)
    },
  })

  // Indicador de filtro activo
  const activeFiltersCount = 
    (statusFilter ? 1 : 0) + 
    (searchTerm ? 1 : 0)

  return (
    <div>
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 py-4">
        <div className="relative w-full sm:max-w-sm">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar por cliente o producto..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9 w-full"
          />
        </div>
        
        <div className="flex items-center gap-2">
          {/* Mostrar indicador de filtros activos */}
          {activeFiltersCount > 0 && (
            <Badge variant="outline" className="flex items-center gap-1">
              <span>Filtros activos: {activeFiltersCount}</span>
              <Button 
                variant="ghost" 
                size="icon" 
                className="h-4 w-4 p-0 hover:bg-transparent"
                onClick={() => {
                  setSearchTerm('')
                  setStatusFilter(null)
                  setColumnFilters([])
                }}
              >
                <span className="sr-only">Limpiar filtros</span>
                ✕
              </Button>
            </Badge>
          )}
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="ml-auto">
                Columnas <ChevronDown className="ml-2 h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {table
                .getAllColumns()
                .filter((column) => column.getCanHide())
                .map((column) => {
                  return (
                    <DropdownMenuCheckboxItem
                      key={column.id}
                      className="capitalize"
                      checked={column.getIsVisible()}
                      onCheckedChange={(value) => column.toggleVisibility(!!value)}
                    >
                      {column.id}
                    </DropdownMenuCheckboxItem>
                  )
                })}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
      <div className="rounded-md border overflow-x-auto">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                    </TableHead>
                  )
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => {
                const isUpdating = updatingOrderIds.has(row.original.id)
                return (
                  <TableRow
                    key={row.id}
                    className={`cursor-pointer hover:bg-muted/50 ${isUpdating ? 'opacity-70' : ''}`}
                    onClick={() => !isUpdating && onSelectOrder(row.original)}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id}>
                        {isUpdating && cell.column.id === 'state' ? (
                          <div className="flex items-center">
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                          </div>
                        ) : (
                          flexRender(cell.column.columnDef.cell, cell.getContext())
                        )}
                      </TableCell>
                    ))}
                  </TableRow>
                )
              })
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  Sin resultados.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-end space-x-2 py-4">
        <div className="flex-1 text-sm text-muted-foreground">
          {table.getFilteredRowModel().rows.length} pedido(s) encontrado(s)
        </div>
        <div className="space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Anterior
          </Button>
          <Button variant="outline" size="sm" onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}>
            Siguiente
          </Button>
        </div>
      </div>
    </div>
  )
}

