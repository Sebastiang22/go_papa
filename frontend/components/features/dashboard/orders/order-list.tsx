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
import { Order, OrderState, OrderCallback, OrderStatusCallback, OrderDeleteCallback } from "@/lib/types"
import { formatDate, formatCOP } from "@/lib/utils/format"

interface OrdersListProps {
  orders: Order[]
  onSelectOrder: OrderCallback
  onStatusUpdate: OrderStatusCallback
  onDeleteOrder: OrderDeleteCallback
  updatingOrderIds?: Set<string>
  setUpdatingOrderIds?: (updater: (prev: Set<string>) => Set<string>) => void
  isLoading?: boolean
  error?: string | null
}

/**
 * Lista de órdenes con funcionalidad de filtrado, ordenamiento y paginación
 */
export function OrdersList({ 
  orders, 
  onSelectOrder, 
  onStatusUpdate, 
  onDeleteOrder, 
  updatingOrderIds = new Set(), 
  setUpdatingOrderIds,
  isLoading = false,
  error = null 
}: OrdersListProps) {
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
        const products = row.getValue("products") as { quantity: number }[]
        const totalItems = products.reduce((sum, product) => sum + product.quantity, 0)
        return <div>{totalItems} item(s)</div>
      },
    },
    {
      id: "total_price",
      header: "Total",
      cell: ({ row }) => {
        const products = row.getValue("products") as { price: number, quantity: number }[]
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
                <span className="sr-only">Filtrar por estado</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleStatusFilterChange(null)}>
                Todos
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => handleStatusFilterChange(OrderState.PENDING)}>
                Pendiente
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleStatusFilterChange(OrderState.PREPARING)}>
                En Preparación
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleStatusFilterChange(OrderState.COMPLETED)}>
                Completado
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      ),
      cell: ({ row }) => {
        return <StatusBadge status={row.getValue("state")} />
      },
    },
    {
      id: "actions",
      cell: ({ row }) => {
        const order = row.original
        const isUpdating = updatingOrderIds.has(order.id);
        
        return (
          <div className="flex items-center justify-end gap-2">
            {/* Acciones de estado */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" disabled={isUpdating}>
                  {isUpdating ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <><Clock className="h-4 w-4" /><span className="sr-only">Estado</span></>
                  )}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem 
                  disabled={order.state === OrderState.PENDING || isUpdating}
                  onClick={() => handleStatusUpdate(order.id, OrderState.PENDING)}
                >
                  <div className="flex items-center">
                    Pendiente
                    {order.state === OrderState.PENDING && <CheckCircle className="ml-2 h-4 w-4 text-green-500" />}
                  </div>
                </DropdownMenuItem>
                <DropdownMenuItem 
                  disabled={order.state === OrderState.PREPARING || isUpdating}
                  onClick={() => handleStatusUpdate(order.id, OrderState.PREPARING)}
                >
                  <div className="flex items-center">
                    En Preparación
                    {order.state === OrderState.PREPARING && <CheckCircle className="ml-2 h-4 w-4 text-green-500" />}
                  </div>
                </DropdownMenuItem>
                <DropdownMenuItem 
                  disabled={order.state === OrderState.COMPLETED || isUpdating}
                  onClick={() => handleStatusUpdate(order.id, OrderState.COMPLETED)}
                >
                  <div className="flex items-center">
                    Completado
                    {order.state === OrderState.COMPLETED && <CheckCircle className="ml-2 h-4 w-4 text-green-500" />}
                  </div>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            
            {/* Botón de eliminar */}
            <Button
              variant="ghost"
              size="icon"
              disabled={isUpdating}
              onClick={() => onDeleteOrder(order.id)}
            >
              <Trash2 className="h-4 w-4 text-red-500" />
              <span className="sr-only">Eliminar</span>
            </Button>
            
            {/* Botón para ver detalles */}
            <Button
              variant="outline"
              size="sm"
              disabled={isUpdating}
              onClick={() => onSelectOrder(order)}
            >
              Ver
            </Button>
          </div>
        )
      },
    },
  ]

  // Función global de búsqueda
  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setSearchTerm(value);
    
    // Aplicar filtro global a través de la API de TanStack Table
    table.setGlobalFilter(value);
  };

  const table = useReactTable({
    data: orders,
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
  })

  // Renderizar estado de carga o error
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-8 space-y-4">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-muted-foreground">Cargando órdenes...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="border border-red-300 bg-red-50 dark:bg-red-900/20 p-4 rounded-md">
        <p className="text-red-500 dark:text-red-400">
          Error: {error}
        </p>
        <Button variant="outline" size="sm" className="mt-4" onClick={() => window.location.reload()}>
          Reintentar
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="text-2xl font-bold tracking-tight">Órdenes</h2>
        <div className="flex items-center gap-2">
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Buscar órdenes..."
              className="w-full pl-8"
              value={searchTerm}
              onChange={handleSearch}
            />
          </div>
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
                      {column.id === 'table_id' ? 'Dirección' : 
                       column.id === 'customer_name' ? 'Cliente' : 
                       column.id === 'total_price' ? 'Total' :
                       column.id === 'created_at' ? 'Fecha' : 
                       column.id === 'state' ? 'Estado' : 
                       column.id}
                    </DropdownMenuCheckboxItem>
                  )
                })}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  )
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                  className="cursor-pointer"
                  onClick={() => onSelectOrder(row.original)}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No se encontraron órdenes
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-between space-x-2 py-4">
        <div className="flex-1 text-sm text-muted-foreground">
          {table.getFilteredRowModel().rows.length} órdenes encontradas.
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Anterior
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Siguiente
          </Button>
        </div>
      </div>
    </div>
  )
} 