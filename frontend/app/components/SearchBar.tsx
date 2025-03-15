import { Input } from "@/components/ui/input"

export default function SearchBar({ onSearch }) {
  return (
    <div className="mb-4">
      <Input type="text" placeholder="Search orders..." onChange={(e) => onSearch(e.target.value)} />
    </div>
  )
}

