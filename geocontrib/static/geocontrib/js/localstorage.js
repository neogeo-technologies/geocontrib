const local = {
    keys() {
      return Object.keys(localStorage);
    },
  
    get(key) {
      const data = localStorage.getItem(key);
      return JSON.parse(data);
    },
  
    set(key, value) {
      localStorage.setItem(key, JSON.stringify(value));
    },
  
    remove(key) {
      localStorage.removeItem(key);
    },
  
    clearAll() {
      localStorage.clear();
    }
  };
  
  class LocalStorage {
    constructor(namespace) {
      this.namespace = namespace;
    }
  
    prefix() {
      return `${this.namespace}.`;
    }
  
    realKey(key) {
      return `${this.prefix()}${key}`;
    }
  
    get(key) {
      return local.get(this.realKey(key));
    }
  
    all() {
      return this.keys()
        .reduce((prev, curr) => {
          prev[curr] = this.get(curr);
          return prev;
        }, {});
    }
  
    keys() {
      const prefix = this.prefix();
      return local.keys()
        .filter(key => key.indexOf(prefix) === 0)
        .map(key => key.replace(prefix, ''));
    }
  
    set(key, value) {
      try {
        local.set(this.realKey(key), value);
      } catch (e) {
        console.log(`set method error: ${JSON.stringify(e)}`);
        return false;
      }
  
      return true;
    }
  
    remove(key) {
      return local.remove(this.realKey(key));
    }
  
    clear() {
      this.keys().forEach(key => this.remove(key));
    }
  
    clearAllStorage() {
      local.clearAll();
    }
  }
