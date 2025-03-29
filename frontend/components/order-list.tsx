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
import { ArrowUpDown, ChevronDown, Search, Loader2, CheckCircle, Clock, Trash2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"

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
}

export function OrderList({ orders, onSelectOrder, onStatusUpdate, onDeleteOrder, updatingOrderIds = new Set() }: OrderListProps) {
  const [sorting, setSorting] = useState<SortingState>([
    { id: "created_at", desc: true }
  ])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({})
  const [searchTerm, setSearchTerm] = useState("")

  const handleStatusUpdate = async (orderId: string, newStatus: string) => {
    // Marcar el pedido como actualizando
    setUpdatingOrderIds(prev => new Set(prev).add(orderId))
    
    try {
      // Llamar a la función de actualización proporcionada por el componente padre
      await onStatusUpdate(orderId, newStatus)
    } finally {
      // Desmarcar el pedido como actualizando
      setUpdatingOrderIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(orderId)
        return newSet
      })
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
      header: "Estado",
      cell: ({ row }) => {
        const status = row.getValue("state") as string
        const orderId = row.original.id
        const isUpdating = updatingOrderIds.has(orderId)
        
        const statusColors = {
          pendiente: "bg-yellow-500",
          "en preparación": "bg-blue-500",
          completado: "bg-green-500",
        }

        return (
          <div className="flex items-center">
            {isUpdating && <Loader2 className="h-4 w-4 mr-2 animate-spin text-muted-foreground" />}
            <Badge className={statusColors[status] || "bg-gray-500"}>
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </Badge>
          </div>
        )
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
    },
    initialState: {
      pagination: {
        pageSize: 10,
      },
    },
  })

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

