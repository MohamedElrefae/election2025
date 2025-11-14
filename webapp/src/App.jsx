import { useState, useEffect } from 'react'
import { createClient } from '@supabase/supabase-js'
import { Users, MapPin, UsersRound } from 'lucide-react'
import * as XLSX from 'xlsx'

const supabaseUrl = 'https://gridbhusfotahmgulgdd.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdyaWRiaHVzZm90YWhtZ3VsZ2RkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI5NDYzNDMsImV4cCI6MjA3ODUyMjM0M30.HXHXIDqepRAyi_BRnVh26rxZBlkksPd84IFH4chgdS0'
const supabase = createClient(supabaseUrl, supabaseKey)

function App() {
  const [activeTab, setActiveTab] = useState('locations')
  const [locations, setLocations] = useState([])
  const [voters, setVoters] = useState([])
  const [families, setFamilies] = useState([])
  const [familyOptions, setFamilyOptions] = useState([])
  const [stats, setStats] = useState({ totalLocations: 0, totalVoters: 0, totalFamilies: 0 })
  const [votersTotal, setVotersTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedLocation, setSelectedLocation] = useState('')
  const [selectedFamily, setSelectedFamily] = useState('')
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 20
  
  // Sorting
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Load stats
      const { count: locCount } = await supabase
        .from('locations')
        .select('*', { count: 'exact', head: true })
      
      const { count: voterCount } = await supabase
        .from('voters')
        .select('*', { count: 'exact', head: true })

      setStats({
        totalLocations: locCount || 0,
        totalVoters: voterCount || 0
      })

      // Load locations
      const { data: locData, error: locError } = await supabase
        .from('locations')
        .select('*')
        .order('location_id', { ascending: true })

      if (locError) throw locError
      setLocations(locData || [])

      // Load family options for filters (top families by size)
      const { data: famOptions, error: famOptionsError } = await supabase
        .from('families_agg')
        .select('*')
        .order('member_count', { ascending: false })
        .limit(500)

      if (famOptionsError) throw famOptionsError
      setFamilyOptions(famOptions || [])

    } catch (err) {
      setError(err.message)
      console.error('Error loading data:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadVoters = async (locationId = null, page = 1, search = '', family = '') => {
    try {
      setLoading(true)
      setError(null)

      const from = (page - 1) * itemsPerPage
      const to = from + itemsPerPage - 1

      let query = supabase
        .from('voters')
        .select('*, locations(location_name, location_number)', { count: 'exact' })

      if (locationId) {
        query = query.eq('location_id', locationId)
      }

      if (family) {
        query = query.eq('family_name', family)
      }

      if (search) {
        const term = `%${search}%`

        const isNumericSearch = !Number.isNaN(Number(search)) && search.trim() !== ''

        if (isNumericSearch) {
          query = query.or(
            `full_name.ilike.${term},first_name.ilike.${term},family_name.ilike.${term},voter_id.eq.${search}`
          )
        } else {
          query = query.or(
            `full_name.ilike.${term},first_name.ilike.${term},family_name.ilike.${term}`
          )
        }
      }

      query = query
        .order('voter_id', { ascending: true })
        .range(from, to)

      const { data, error, count } = await query

      if (error) throw error

      setVoters(data || [])
      setVotersTotal(count || 0)
      setStats(prev => ({
        ...prev,
        totalVoters: count ?? prev.totalVoters
      }))
    } catch (err) {
      setError(err.message)
      console.error('Error loading voters:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadFamilies = async (page = 1, search = '') => {
    try {
      setLoading(true)
      setError(null)

      const from = (page - 1) * itemsPerPage
      const to = from + itemsPerPage - 1

      let query = supabase
        .from('families_agg')
        .select('*', { count: 'exact' })

      if (search) {
        const term = `%${search}%`
        query = query.ilike('family_name', term)
      }

      const { data, error, count } = await query
        .order('member_count', { ascending: false })
        .range(from, to)

      if (error) throw error

      setFamilies(data || [])
      setStats(prev => ({ ...prev, totalFamilies: count || 0 }))
    } catch (err) {
      setError(err.message)
      console.error('Error loading families:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (activeTab === 'voters') {
      loadVoters(selectedLocation || null, currentPage, searchTerm, selectedFamily)
    } else if (activeTab === 'families') {
      loadFamilies(currentPage, searchTerm)
    }
  }, [activeTab, selectedLocation, currentPage, searchTerm, selectedFamily])

  const filteredLocations = locations.filter(loc =>
    loc.location_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    loc.location_address?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    loc.location_number?.toString().includes(searchTerm)
  )

  const filteredVoters = voters.filter(voter =>
    (voter.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    voter.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    voter.family_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    voter.voter_id?.toString().includes(searchTerm)) &&
    (!selectedFamily || voter.family_name === selectedFamily)
  )

  const filteredFamilies = families.filter(family =>
    family.family_name?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  // Sorting function
  const handleSort = (key) => {
    let direction = 'asc'
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc'
    }
    setSortConfig({ key, direction })
  }

  // Apply sorting
  const sortedLocations = [...filteredLocations].sort((a, b) => {
    if (!sortConfig.key) return 0
    
    const aValue = a[sortConfig.key]
    const bValue = b[sortConfig.key]
    
    if (aValue === null || aValue === undefined) return 1
    if (bValue === null || bValue === undefined) return -1
    
    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue
    }
    
    const aStr = String(aValue).toLowerCase()
    const bStr = String(bValue).toLowerCase()
    
    if (sortConfig.direction === 'asc') {
      return aStr.localeCompare(bStr, 'ar')
    } else {
      return bStr.localeCompare(aStr, 'ar')
    }
  })

  const sortedVoters = [...filteredVoters].sort((a, b) => {
    if (!sortConfig.key) return 0
    
    let aValue, bValue
    
    if (sortConfig.key === 'location_name') {
      aValue = a.locations?.location_name
      bValue = b.locations?.location_name
    } else if (sortConfig.key === 'location_number') {
      aValue = a.locations?.location_number
      bValue = b.locations?.location_number
    } else {
      aValue = a[sortConfig.key]
      bValue = b[sortConfig.key]
    }
    
    if (aValue === null || aValue === undefined) return 1
    if (bValue === null || bValue === undefined) return -1
    
    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue
    }
    
    const aStr = String(aValue).toLowerCase()
    const bStr = String(bValue).toLowerCase()
    
    if (sortConfig.direction === 'asc') {
      return aStr.localeCompare(bStr, 'ar')
    } else {
      return bStr.localeCompare(aStr, 'ar')
    }
  })

  const sortedFamilies = [...filteredFamilies].sort((a, b) => {
    if (!sortConfig.key) return 0
    
    const aValue = a[sortConfig.key]
    const bValue = b[sortConfig.key]
    
    if (aValue === null || aValue === undefined) return 1
    if (bValue === null || bValue === undefined) return -1
    
    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue
    }
    
    const aStr = String(aValue).toLowerCase()
    const bStr = String(bValue).toLowerCase()
    
    if (sortConfig.direction === 'asc') {
      return aStr.localeCompare(bStr, 'ar')
    } else {
      return bStr.localeCompare(aStr, 'ar')
    }
  })

  const paginatedLocations = sortedLocations.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  const paginatedVoters = sortedVoters

  const paginatedFamilies = sortedFamilies

  const totalPages = Math.ceil(
    (activeTab === 'locations'
      ? sortedLocations.length
      : activeTab === 'voters'
        ? (stats.totalVoters || sortedVoters.length)
        : (stats.totalFamilies || sortedFamilies.length)
    ) / itemsPerPage
  )

  const getSortIcon = (columnKey) => {
    if (sortConfig.key !== columnKey) {
      return ' ⇅'
    }
    return sortConfig.direction === 'asc' ? ' ↑' : ' ↓'
  }

  const handlePrint = () => {
    window.print()
  }

  const handlePrintReport = () => {
    try {
      const table = document.querySelector('table')
      if (!table) return

      const title =
        activeTab === 'locations'
          ? 'تقرير المواقع الانتخابية'
          : activeTab === 'voters'
            ? 'تقرير الناخبين'
            : 'تقرير العائلات'

      const now = new Date()
      const dateStr = now.toLocaleString('ar-EG')

      // Hide the entire original UI
      const body = document.body
      const bodyChildren = Array.from(body.children)
      bodyChildren.forEach(child => {
        child.style.display = 'none'
      })

      // Create a clean, minimal DOM structure for printing
      const printContainer = document.createElement('div')
      printContainer.className = 'print-container'
      printContainer.style.direction = 'rtl'
      printContainer.className = 'print-container'
      printContainer.innerHTML = `
        <div class="print-header">
          <h1>${title}</h1>
          <div class="meta">${dateStr}</div>
        </div>
        <div class="table-container">
          ${table.outerHTML}
        </div>
      `
      
      // Add the clean content to body
      body.appendChild(printContainer)
      
      // Give the browser a moment to layout before printing
      setTimeout(() => {
        window.print()
        
        // Restore original UI
        setTimeout(() => {
          body.removeChild(printContainer)
          bodyChildren.forEach(child => {
            child.style.display = ''
          })
        }, 100)
      }, 100)
    } catch (err) {
      console.error('Error preparing print:', err)
      alert('حدث خطأ أثناء تجهيز صفحة الطباعة')
      // Restore UI in case of error
      Array.from(document.body.children).forEach(child => {
        child.style.display = ''
      })
    }
  }
  const handleExportExcel = () => {
    try {
      const workbook = XLSX.utils.book_new()

      const buildSheet = (header, rows) => {
        const worksheet = XLSX.utils.aoa_to_sheet([header, ...rows])

        // Auto column widths based on Arabic content length
        const colWidths = header.map((_, colIndex) => {
          const headerLen = header[colIndex] ? header[colIndex].toString().length : 0
          const maxCellLen = rows.reduce((max, row) => {
            const cell = row[colIndex]
            const len = cell != null ? cell.toString().length : 0
            return Math.max(max, len)
          }, 0)
          const maxLen = Math.max(headerLen, maxCellLen)
          return { wch: Math.min(Math.max(maxLen + 2, 10), 40) }
        })
        worksheet['!cols'] = colWidths

        // Enable filters on header row
        const columnLetter = (colIndex) => {
          let letter = ''
          let n = colIndex + 1
          while (n > 0) {
            const rem = (n - 1) % 26
            letter = String.fromCharCode(65 + rem) + letter
            n = Math.floor((n - 1) / 26)
          }
          return letter
        }

        const lastColLetter = columnLetter(header.length - 1)
        const lastRowIndex = rows.length + 1 // including header
        worksheet['!autofilter'] = { ref: `A1:${lastColLetter}${lastRowIndex}` }

        return worksheet
      }

      // المواقع sheet
      if (sortedLocations.length > 0) {
        const header = ['رقم الموقع', 'اسم الموقع', 'العنوان', 'عدد الناخبين']
        const rows = sortedLocations.map(loc => [
          loc.location_number,
          loc.location_name,
          loc.location_address,
          loc.total_voters ?? 0
        ])
        const wsLocations = buildSheet(header, rows)
        XLSX.utils.book_append_sheet(workbook, wsLocations, 'المواقع')
      }

      // الناخبين sheet (current loaded voters)
      if (sortedVoters.length > 0) {
        const header = ['رقم الناخب', 'الاسم الكامل', 'اسم العائلة', 'رقم الموقع', 'اسم الموقع']
        const rows = sortedVoters.map(voter => [
          voter.voter_id,
          voter.full_name,
          voter.family_name,
          voter.locations?.location_number,
          voter.locations?.location_name
        ])
        const wsVoters = buildSheet(header, rows)
        XLSX.utils.book_append_sheet(workbook, wsVoters, 'الناخبين')
      }

      // العائلات sheet
      if (sortedFamilies.length > 0) {
        const header = ['اسم العائلة', 'عدد الأفراد', 'عدد المواقع']
        const rows = sortedFamilies.map(fam => [
          fam.family_name,
          fam.member_count,
          fam.location_count
        ])
        const wsFamilies = buildSheet(header, rows)
        XLSX.utils.book_append_sheet(workbook, wsFamilies, 'العائلات')
      }

      XLSX.writeFile(workbook, 'election-report.xlsx')
    } catch (err) {
      console.error('Error exporting Excel:', err)
      alert('حدث خطأ أثناء تصدير ملف Excel')
    }
  }

  return (
    <div className="app">
      <div className="container">
        <div className="header">
          <div className="header-actions">
            <div>
              <h1>🗳️ إدارة بيانات الانتخابات - مطوبس 2025</h1>
              <p>نظام إدارة قاعدة بيانات الناخبين - محافظة كفر الشيخ</p>
            </div>
            <div className="header-buttons">
              <button className="action-button" type="button" onClick={handleExportExcel}>
                تصدير Excel
              </button>
              <button className="action-button" type="button" onClick={handlePrintReport}>
                تجهيز PDF للطباعة
              </button>
              <button className="action-button primary" type="button" onClick={handlePrint}>
                طباعة الصفحة الحالية
              </button>
            </div>
          </div>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <h3>إجمالي المواقع</h3>
            <div className="value">{stats.totalLocations.toLocaleString()}</div>
          </div>
          <div className="stat-card">
            <h3>إجمالي الناخبين</h3>
            <div className="value">{stats.totalVoters.toLocaleString()}</div>
          </div>
          <div className="stat-card">
            <h3>إجمالي العائلات</h3>
            <div className="value">{(stats.totalFamilies || 0).toLocaleString()}</div>
          </div>
          <div className="stat-card">
            <h3>متوسط الناخبين لكل موقع</h3>
            <div className="value">
              {stats.totalLocations > 0 
                ? Math.round(stats.totalVoters / stats.totalLocations).toLocaleString()
                : 0}
            </div>
          </div>
        </div>

        <div className="tabs">
          <button
            className={`tab ${activeTab === 'locations' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('locations')
              setCurrentPage(1)
              setSearchTerm('')
              setSortConfig({ key: null, direction: 'asc' })
            }}
          >
            <MapPin size={18} style={{ display: 'inline', marginLeft: '8px' }} />
            المواقع الانتخابية
          </button>
          <button
            className={`tab ${activeTab === 'voters' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('voters')
              setCurrentPage(1)
              setSearchTerm('')
              setSortConfig({ key: null, direction: 'asc' })
            }}
          >
            <Users size={18} style={{ display: 'inline', marginLeft: '8px' }} />
            الناخبين
          </button>
          <button
            className={`tab ${activeTab === 'families' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('families')
              setCurrentPage(1)
              setSearchTerm('')
              setSelectedFamily('')
              setSortConfig({ key: null, direction: 'asc' })
            }}
          >
            <UsersRound size={18} style={{ display: 'inline', marginLeft: '8px' }} />
            العائلات
          </button>
        </div>

        <div className="content-card">
          {error && <div className="error">خطأ: {error}</div>}

          <div className="filters">
            <input
              type="text"
              className="search-input"
              placeholder={
                activeTab === 'locations' ? 'بحث في المواقع...' : 
                activeTab === 'voters' ? 'بحث في الناخبين...' : 
                'بحث في العائلات...'
              }
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value)
                setCurrentPage(1)
              }}
            />
            
            {activeTab === 'voters' && (
              <>
                <select
                  className="select"
                  value={selectedLocation}
                  onChange={(e) => {
                    setSelectedLocation(e.target.value)
                    setCurrentPage(1)
                  }}
                >
                  <option value="">جميع المواقع</option>
                  {locations.map(loc => (
                    <option key={loc.location_id} value={loc.location_id}>
                      {loc.location_number} - {loc.location_name}
                    </option>
                  ))}
                </select>
                <select
                  className="select"
                  value={selectedFamily}
                  onChange={(e) => {
                    setSelectedFamily(e.target.value)
                    setCurrentPage(1)
                  }}
                >
                  <option value="">جميع العائلات</option>
                  {familyOptions.slice(0, 100).map((fam, idx) => (
                    <option key={idx} value={fam.family_name}>
                      {fam.family_name} ({fam.member_count})
                    </option>
                  ))}
                </select>
              </>
            )}
          </div>

          {loading ? (
            <div className="loading">
              <div>جاري التحميل...</div>
              <div style={{ fontSize: '0.875rem', marginTop: '10px', color: '#718096' }}>
                {activeTab === 'voters' && voters.length > 0 && `تم تحميل ${voters.length.toLocaleString()} ناخب...`}
                {activeTab === 'families' && families.length > 0 && `تم تحميل ${families.length.toLocaleString()} عائلة...`}
              </div>
            </div>
          ) : activeTab === 'families' ? (
            <>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th 
                        onClick={() => handleSort('family_name')}
                        style={{ cursor: 'pointer' }}
                      >
                        اسم العائلة{getSortIcon('family_name')}
                      </th>
                      <th 
                        onClick={() => handleSort('member_count')}
                        style={{ cursor: 'pointer' }}
                      >
                        عدد الأفراد{getSortIcon('member_count')}
                      </th>
                      <th 
                        onClick={() => handleSort('location_count')}
                        style={{ cursor: 'pointer' }}
                      >
                        عدد المواقع{getSortIcon('location_count')}
                      </th>
                      <th>إجراءات</th>
                    </tr>
                  </thead>
                  <tbody>
                    {paginatedFamilies.map((family, idx) => (
                      <tr key={idx}>
                        <td><strong>{family.family_name}</strong></td>
                        <td><span className="badge">{family.member_count.toLocaleString()}</span></td>
                        <td>{family.location_count}</td>
                        <td>
                          <button
                            className="view-button"
                            onClick={() => {
                              setActiveTab('voters')
                              setSelectedFamily(family.family_name)
                              setSearchTerm('')
                              setCurrentPage(1)
                            }}
                          >
                            عرض الأفراد
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {filteredFamilies.length === 0 && (
                <div className="loading">لا توجد نتائج</div>
              )}
            </>
          ) : activeTab === 'locations' ? (
            <>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th 
                        onClick={() => handleSort('location_number')}
                        style={{ cursor: 'pointer' }}
                      >
                        رقم الموقع{getSortIcon('location_number')}
                      </th>
                      <th 
                        onClick={() => handleSort('location_name')}
                        style={{ cursor: 'pointer' }}
                      >
                        اسم الموقع{getSortIcon('location_name')}
                      </th>
                      <th 
                        onClick={() => handleSort('location_address')}
                        style={{ cursor: 'pointer' }}
                      >
                        العنوان{getSortIcon('location_address')}
                      </th>
                      <th 
                        onClick={() => handleSort('total_voters')}
                        style={{ cursor: 'pointer' }}
                      >
                        عدد الناخبين{getSortIcon('total_voters')}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {paginatedLocations.map(location => (
                      <tr key={location.location_id}>
                        <td><span className="badge">{location.location_number}</span></td>
                        <td>{location.location_name}</td>
                        <td>{location.location_address}</td>
                        <td><strong>{location.total_voters?.toLocaleString() || 0}</strong></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {filteredLocations.length === 0 && (
                <div className="loading">لا توجد نتائج</div>
              )}
            </>
          ) : (
            <>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th 
                        onClick={() => handleSort('voter_id')}
                        style={{ cursor: 'pointer' }}
                      >
                        رقم الناخب{getSortIcon('voter_id')}
                      </th>
                      <th 
                        onClick={() => handleSort('full_name')}
                        style={{ cursor: 'pointer' }}
                      >
                        الاسم الكامل{getSortIcon('full_name')}
                      </th>
                      <th 
                        onClick={() => handleSort('family_name')}
                        style={{ cursor: 'pointer' }}
                      >
                        اسم العائلة{getSortIcon('family_name')}
                      </th>
                      <th 
                        onClick={() => handleSort('location_name')}
                        style={{ cursor: 'pointer' }}
                      >
                        الموقع{getSortIcon('location_name')}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {paginatedVoters.map(voter => (
                      <tr key={voter.id}>
                        <td><span className="badge">{voter.voter_id}</span></td>
                        <td>{voter.full_name}</td>
                        <td><strong>{voter.family_name}</strong></td>
                        <td>
                          {voter.locations?.location_number} - {voter.locations?.location_name}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {filteredVoters.length === 0 && (
                <div className="loading">لا توجد نتائج</div>
              )}
            </>
          )}

          {totalPages > 1 && (
            <div className="pagination">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
              >
                السابق
              </button>
              <span>
                صفحة {currentPage} من {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
              >
                التالي
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
