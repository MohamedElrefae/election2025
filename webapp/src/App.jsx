import { useState, useEffect } from 'react'
import { createClient } from '@supabase/supabase-js'
import { Users, MapPin, UsersRound } from 'lucide-react'

const supabaseUrl = 'https://gridbhusfotahmgulgdd.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdyaWRiaHVzZm90YWhtZ3VsZ2RkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI5NDYzNDMsImV4cCI6MjA3ODUyMjM0M30.HXHXIDqepRAyi_BRnVh26rxZBlkksPd84IFH4chgdS0'
const supabase = createClient(supabaseUrl, supabaseKey)

function App() {
  const [activeTab, setActiveTab] = useState('locations')
  const [locations, setLocations] = useState([])
  const [voters, setVoters] = useState([])
  const [families, setFamilies] = useState([])
  const [stats, setStats] = useState({ totalLocations: 0, totalVoters: 0, totalFamilies: 0 })
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

    } catch (err) {
      setError(err.message)
      console.error('Error loading data:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadVoters = async (locationId = null) => {
    try {
      setLoading(true)
      
      // Load all voters with pagination
      let allVoters = []
      let page = 0
      const pageSize = 1000
      let hasMore = true

      while (hasMore) {
        let query = supabase
          .from('voters')
          .select('*, locations(location_name, location_number)')
          .order('voter_id', { ascending: true })
          .range(page * pageSize, (page + 1) * pageSize - 1)

        if (locationId) {
          query = query.eq('location_id', locationId)
        }

        const { data, error } = await query

        if (error) throw error
        
        if (data && data.length > 0) {
          allVoters = [...allVoters, ...data]
          page++
          hasMore = data.length === pageSize
        } else {
          hasMore = false
        }
      }

      setVoters(allVoters)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadFamilies = async () => {
    try {
      setLoading(true)
      
      // Load all voters with family names using pagination
      let allVoters = []
      let page = 0
      const pageSize = 1000
      let hasMore = true

      while (hasMore) {
        const { data, error } = await supabase
          .from('voters')
          .select('family_name, location_id, locations(location_name)')
          .not('family_name', 'is', null)
          .not('family_name', 'eq', '')
          .range(page * pageSize, (page + 1) * pageSize - 1)

        if (error) throw error

        if (data && data.length > 0) {
          allVoters = [...allVoters, ...data]
          page++
          hasMore = data.length === pageSize
        } else {
          hasMore = false
        }
      }

      // Group by family name
      const familyMap = {}
      allVoters.forEach(voter => {
        const familyName = voter.family_name
        if (!familyMap[familyName]) {
          familyMap[familyName] = {
            family_name: familyName,
            member_count: 0,
            locations: new Set()
          }
        }
        familyMap[familyName].member_count++
        familyMap[familyName].locations.add(voter.location_id)
      })

      // Convert to array and sort by member count
      const familiesArray = Object.values(familyMap).map(f => ({
        ...f,
        location_count: f.locations.size,
        locations: Array.from(f.locations)
      })).sort((a, b) => b.member_count - a.member_count)

      setFamilies(familiesArray)
      setStats(prev => ({ ...prev, totalFamilies: familiesArray.length }))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (activeTab === 'voters') {
      loadVoters(selectedLocation || null)
    } else if (activeTab === 'families') {
      loadFamilies()
    }
  }, [activeTab, selectedLocation])

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

  const paginatedVoters = sortedVoters.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  const paginatedFamilies = sortedFamilies.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  const totalPages = Math.ceil(
    (activeTab === 'locations' ? sortedLocations.length : 
     activeTab === 'voters' ? sortedVoters.length : 
     sortedFamilies.length) / itemsPerPage
  )

  const getSortIcon = (columnKey) => {
    if (sortConfig.key !== columnKey) {
      return ' ⇅'
    }
    return sortConfig.direction === 'asc' ? ' ↑' : ' ↓'
  }

  return (
    <div className="app">
      <div className="container">
        <div className="header">
          <h1>🗳️ إدارة بيانات الانتخابات - مطوبس 2025</h1>
          <p>نظام إدارة قاعدة بيانات الناخبين - محافظة كفر الشيخ</p>
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
                  {families.slice(0, 100).map((fam, idx) => (
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
