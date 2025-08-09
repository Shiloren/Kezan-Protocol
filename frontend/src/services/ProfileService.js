class ProfileService {
  constructor(baseUrl = 'http://localhost:5000/api') {
    this.baseUrl = baseUrl;
  }

  async getProfile(version) {
    const response = await fetch(`${this.baseUrl}/profile/${version}`);
    if (!response.ok) throw new Error('Error al obtener el perfil');
    return response.json();
  }

  async updateProfile(version, preferences) {
    const response = await fetch(`${this.baseUrl}/profile/${version}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(preferences),
    });
    if (!response.ok) throw new Error('Error al actualizar el perfil');
    return response.json();
  }

  async addWatchedItem(version, itemId, maxPrice = null) {
    const response = await fetch(`${this.baseUrl}/profile/${version}/items`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ itemId, maxPrice }),
    });
    if (!response.ok) throw new Error('Error al añadir el item');
    return response.json();
  }

  async removeWatchedItem(version, itemId) {
    const response = await fetch(`${this.baseUrl}/profile/${version}/items/${itemId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Error al eliminar el item');
    return response.json();
  }

  async updatePriceThreshold(version, itemId, maxPrice) {
    const response = await fetch(`${this.baseUrl}/profile/${version}/items/${itemId}/threshold`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ maxPrice }),
    });
    if (!response.ok) throw new Error('Error al actualizar el umbral de precio');
    return response.json();
  }

  async getPriceHistory(version, itemId) {
    const response = await fetch(`${this.baseUrl}/profile/${version}/items/${itemId}/history`);
    if (!response.ok) throw new Error('Error al obtener el historial de precios');
    return response.json();
  }
}

export default ProfileService;
