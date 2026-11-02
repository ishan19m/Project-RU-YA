export const kpis = { revenue: 1967879556.46, units: 55818, aov: 69728.56, growth: 8.4, margin: 13.08 }
export const monthly = [
  ['Jan','142.5','150.1'],['Feb','151.8','158.4'],['Mar','159.2','163.8'],['Apr','154.7','161.3'],['May','169.8','172.5'],['Jun','174.3','178.2'],['Jul','181.5','184.9'],['Aug','177.2','181.7'],['Sep','186.8','191.2'],['Oct','193.7','199.6'],['Nov','201.3','207.1'],['Dec','219.8','226.4']
].map(([month, actual, forecast]) => ({ month, actual: Number(actual), forecast: Number(forecast) }))
export const categories = [{name:'Electronics', value:38, color:'#C6A56B'},{name:'Home Appliances',value:24,color:'#4C9B7A'},{name:'Mobile & Accessories',value:21,color:'#789C86'},{name:'Computing',value:17,color:'#61736a'}]
export const products = [{name:'Samsung Galaxy S24', category:'Mobile & Accessories', revenue:'₹12.8M', units:'1,284', change:'+18.6%'},{name:'LG 55” OLED Smart TV', category:'Electronics', revenue:'₹9.4M', units:'382', change:'+12.2%'},{name:'Apple MacBook Air M3', category:'Computing', revenue:'₹8.7M', units:'246', change:'+9.8%'},{name:'Dyson V12 Detect Slim', category:'Home Appliances', revenue:'₹5.2M', units:'319', change:'+7.4%'}]
