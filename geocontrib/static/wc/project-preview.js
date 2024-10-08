const base64defaultImg = `data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMzMiIGhlaWdodD0iMjUwIiBzdHlsZT0ic2hhcGUtcmVuZGVyaW5nOmdlb21ldHJpY1ByZWNpc2lvbjt0ZXh0LXJlbmRlcmluZzpnZW9tZXRyaWNQcmVjaXNpb247aW1hZ2UtcmVuZGVyaW5nOm9wdGltaXplUXVhbGl0eTtmaWxsLXJ1bGU6ZXZlbm9kZDtjbGlwLXJ1bGU6ZXZlbm9kZCI+PHBhdGggc3R5bGU9Im9wYWNpdHk6MSIgZmlsbD0iIzIyMiIgZD0iTS0uNS0uNWgzMzN2MjUwSC0uNVYtLjV6Ii8+PHBhdGggc3R5bGU9Im9wYWNpdHk6MSIgZmlsbD0iI2ZiZmJmYiIgZD0iTTExNS41IDg1LjVoMTAxdjc4aC0xMDF2LTc4eiIvPjxwYXRoIHN0eWxlPSJvcGFjaXR5OjEiIGZpbGw9IiMxNjE2MTYiIGQ9Ik0xMjUuNSA5NS41aDgxdjU4aC04MXYtNTh6Ii8+PHBhdGggc3R5bGU9Im9wYWNpdHk6MSIgZmlsbD0iIzIyMiIgZD0iTTEyNi41IDk2LjVoNzl2NTZoLTc5di01NnoiLz48cGF0aCBzdHlsZT0ib3BhY2l0eToxIiBmaWxsPSIjZjZmNmY2IiBkPSJNMTM3LjUgMTAzLjVjOS4xNTgtMS42NjUgMTMuMzI1IDIuMDAxIDEyLjUgMTEtNC42MDggNy4wNC05Ljk0MSA3LjcwNy0xNiAyLTIuNjUyLTUuNDYxLTEuNDg2LTkuNzk0IDMuNS0xM3oiLz48cGF0aCBzdHlsZT0ib3BhY2l0eToxIiBmaWxsPSIjZjdmN2Y3IiBkPSJNMTk1LjUgMTQ0LjVjLTMuMTI1Ljk3OS02LjQ1OCAxLjMxMy0xMCAxYTc0MjkuMjg2IDc0MjkuMjg2IDAgMCAxLTExLjUtMTlsLTkuNSAxMy41Yy0zLjA0OS0uNzc4LTUuODgyLTIuMjc4LTguNS00LjVhMTA1LjM1MyAxMDUuMzUzIDAgMCAwLTcuNSAxMGMtMy44NzEuMzE1LTcuNTM4LS4wMTgtMTEtMWExNzQuMzM4IDE3NC4zMzggMCAwIDEgMTYuNS0yMmw3IDVhNzU4NC4yMiA3NTg0LjIyIDAgMCAxIDEzLjUtMTkgNDgxLjA3OSA0ODEuMDc5IDAgMCAxIDIxIDM2eiIvPjxwYXRoIHN0eWxlPSJvcGFjaXR5OjEiIGZpbGw9IiM5Nzk3OTciIGQ9Ik0xMzcuNSAxNDQuNWMzLjQ2Mi45ODIgNy4xMjkgMS4zMTUgMTEgMS0zLjg1MSAxLjMwOS03Ljg1MSAxLjMwOS0xMiAwIC4xMjQtLjYwNy40NTctLjk0IDEtMXoiLz48cGF0aCBzdHlsZT0ib3BhY2l0eToxIiBmaWxsPSIjOGY4ZjhmIiBkPSJNMTk1LjUgMTQ0LjVjLjU0My4wNi44NzYuMzkzIDEgMS0zLjgxNSAxLjMwOC03LjQ4MSAxLjMwOC0xMSAwIDMuNTQyLjMxMyA2Ljg3NS0uMDIxIDEwLTF6Ii8+PHBhdGggc3R5bGU9Im9wYWNpdHk6MSIgZmlsbD0iI2FmYWZhZiIgZD0iTTEyNS41IDk1LjV2NThoODFhMTY4MS44IDE2ODEuOCAwIDAgMS04MiAxYy0uMzMtMTkuODQuMDAzLTM5LjUwNyAxLTU5eiIvPjwvc3ZnPg==`;
const base64userImg = `data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiA/Pgo8c3ZnIHZpZXdCb3g9IjAgMCA1MTIgNTEyIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgogICAgPHBhdGggZmlsbD0iIzY2NjY2NiIgZD0iTTI1NiAyODhjNzkuNSAwIDE0NC02NC41IDE0NC0xNDRTMzM1LjUgMCAyNTYgMCAxMTIgNjQuNSAxMTIgMTQ0czY0LjUgMTQ0IDE0NCAxNDR6bTEyOCAzMmgtNTUuMWMtMjIuMiAxMC4yLTQ2LjkgMTYtNzIuOSAxNnMtNTAuNi01LjgtNzIuOS0xNkgxMjhDNTcuMyAzMjAgMCAzNzcuMyAwIDQ0OHYxNmMwIDI2LjUgMjEuNSA0OCA0OCA0OGg0MTZjMjYuNSAwIDQ4LTIxLjUgNDgtNDh2LTE2YzAtNzAuNy01Ny4zLTEyOC0xMjgtMTI4eiIvPgo8L3N2Zz4=`
const base64featureImg = `data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiA/Pgo8c3ZnIHZpZXdCb3g9IjAgMCAzODQgNTEyIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgogICAgPHBhdGggZmlsbD0iIzY2NjY2NiIgZD0iTTE3Mi4yNjggNTAxLjY3QzI2Ljk3IDI5MS4wMzEgMCAyNjkuNDEzIDAgMTkyIDAgODUuOTYxIDg1Ljk2MSAwIDE5MiAwczE5MiA4NS45NjEgMTkyIDE5MmMwIDc3LjQxMy0yNi45NyA5OS4wMzEtMTcyLjI2OCAzMDkuNjctOS41MzUgMTMuNzc0LTI5LjkzIDEzLjc3My0zOS40NjQgMHoiLz4KPC9zdmc+`
const base64commentImg = `data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiA/Pgo8c3ZnIHZpZXdCb3g9IjAgMCA1MTIgNTEyIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgogICAgPHBhdGggZmlsbD0iIzY2NjY2NiIgZD0iTTI1NiAzMkMxMTQuNiAzMiAuMDI3MiAxMjUuMSAuMDI3MiAyNDBjMCA0OS42MyAyMS4zNSA5NC45OCA1Ni45NyAxMzAuN2MtMTIuNSA1MC4zNy01NC4yNyA5NS4yNy01NC43NyA5NS43N2MtMi4yNSAyLjI1LTIuODc1IDUuNzM0LTEuNSA4LjczNEMxLjk3OSA0NzguMiA0Ljc1IDQ4MCA4IDQ4MGM2Ni4yNSAwIDExNS4xLTMxLjc2IDE0MC42LTUxLjM5QzE4MS4yIDQ0MC45IDIxNy42IDQ0OCAyNTYgNDQ4YzE0MS40IDAgMjU1LjEtOTMuMTMgMjU1LjEtMjA4UzM5Ny40IDMyIDI1NiAzMnoiLz4KPC9zdmc+`

// Define the Web Component
class ProjectPreview extends HTMLElement {
    constructor() {
      super();
      // Use the Shadow DOM to encapsulate component styles and structure
      this.attachShadow({ mode: 'open' });
      // Default configuration for width, color, and font
      this.config = {
        width: '500px',
        color: '#008c86',
        font: "'Roboto Condensed', 'Lato', 'Helvetica Neue'"
      };
    }
  
    // Called when the component is added to the DOM
    connectedCallback() {
      // Check for user-defined attributes and update the default config accordingly
      Object.keys(this.config).forEach(attr => {
        if (this.getAttribute(attr)) {
          this.config[attr] = this.getAttribute(attr);
        }
      });
      // Retrieve domain and project slug from attributes
      const domain = this.getAttribute('domain');
      const projectSlug = this.getAttribute('project-slug');
      // Render the initial structure of the component
      this.render();
  
      // Handle errors if required attributes are missing
      if (!domain) {
        this.shadowRoot.querySelector('#project-name').textContent = 'Erreur: Domaine inconnu';
        this.shadowRoot.querySelector('#project-description').textContent = 'Veuillez renseigner un domaine.';
      } else if (!projectSlug) {
        this.shadowRoot.querySelector('#project-name').textContent = 'Erreur: Projet inconnu';
        this.shadowRoot.querySelector('#project-description').textContent = 'Veuillez renseigner un slug projet.';
        } else {
        // Fetch project data from the API and update the component
        fetch(`${domain}/geocontrib/api/v2/projects/${projectSlug}/`)
          .then(response => response.json())
          .then(data => {
            this.updateComponent(domain, data);
          })
          .catch(error => {
            // Handle any errors that occur during the fetch request
            console.error('Error fetching data:', error);
            this.shadowRoot.querySelector('#project-name').textContent = 'Erreur de chargement';
        });
      }
    }
  
    // Function to render the initial component structure
    render() {
      this.shadowRoot.innerHTML = `
        <style>
          .project-preview {
            width: ${this.config.width};
            height: 150px;
            border-radius: 1.5rem;
            padding: 1.5rem;
            margin: 1rem;
            display: flex;
            transition: all ease .2s;
            font-family: ${this.config.font}, Arial, Helvetica, sans-serif;
          }
          .project-preview:link, .project-preview:visited, .project-preview:hover, .project-preview:active {
            text-decoration: none;
            box-shadow: 0 1px 2px 0 rgba(34,36,38,.12),0 1px 5px 0 rgba(34,36,38,.15);
          }
          .project-preview:hover {
            border: 1px solid #ccc;
            box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.15);
          }
          .project-thumbnail {
            width: 40%;
          }
          .project-thumbnail img {
            height: 100%;
            width: 100%;
            object-fit: cover;
          }
          .project-details {
            width: 60%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
          }
          .project-details * {
            overflow: hidden;
            text-overflow: ellipsis;
          }
          .project-details > * {
            margin: .2rem 0 .2rem 1rem;
          }
          .project-details > *:first-child {
            margin-top: -.25rem;
          }
          .project-details > *:last-child {
            margin-bottom: -.25rem;
          }
          .project-details h1 {
            white-space: nowrap;
            font-size: 1.2em;
            color: ${this.config.color};
          }
          .project-details p {
            font-size: 0.9em;
            color: #555;
            /* keep descripton on 2 lines max */
            word-break: break-all;
            display: -webkit-box;
            -webkit-box-orient: vertical;
            -moz-box-orient: vertical;
            -ms-box-orient: vertical;
            box-orient: vertical;
            -webkit-line-clamp: 2;
            -moz-line-clamp: 2;
            -ms-line-clamp: 2;
            line-clamp: 2;
            overflow: hidden;
          }
          .project-details .stats {
            display: flex;
            justify-content: space-between;
            gap: .5em;
            text-align: center;
          }
          .project-details .stats > div {
            flex: 1 1 0px;
          }
          .project-details .stats img {
            height: 20px;
            margin-bottom: .2em;
          }
          .project-details .stats .number {
            color: ${this.config.color};
          }
          .project-details .stats small {
            color: #666;
          }
          /* Light mode */
          @media (prefers-color-scheme: light) {
            .project-preview {
              background-color: #fff;
              border: 1px solid #ddd;
            }
          }
          /* Dark mode */
          @media (prefers-color-scheme: dark) {
            .project-preview {
              background-color: #111;
              color: #fff;
              border: 1px solid #222;
            }
            .project-preview:hover {
              border: 1px solid ${this.config.color};
              box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.15);
            }
            .project-details p {
              color: #eee;
            }
            .project-details .stats small {
              color: #ddd;
            }
          }
        </style>

        <a class="project-preview" href="#">
          <div class="project-thumbnail">
            <img id="project-image" src="${base64defaultImg}" alt="">
          </div>
          <article class="project-details">
            <h1 id="project-name">Chargement...</h1>
            <p id="project-description"></p>
            <div class="stats" id="project-statistics">
              <div id="project-members">
                <img src="${base64userImg}" alt="">
                <div class="number">0</div>
                <small>Membres</small>
              </div>
              <div id="project-features">
                <img src="${base64featureImg}" alt="">
                <div class="number">0</div>
                <small>Signalements</small>
              </div>
              <div id="project-comments">
                <img src="${base64commentImg}" alt="">
                <div class="number">0</div>
                <small>Commentaires</small>
              </div>
            </div>
          </article>
        </a>
      `;
    }
  
    // Update the component with data fetched from the API
    updateComponent(domain, data) {
      // Set project details based on the fetched data
      this.shadowRoot.querySelector('#project-image').src = domain + data.thumbnail;
      this.shadowRoot.querySelector('#project-name').textContent = data.title;
      this.shadowRoot.querySelector('#project-description').textContent = data.description;
      this.shadowRoot.querySelector('#project-members .number').textContent = data.nb_contributors;
      this.shadowRoot.querySelector('#project-features .number').textContent = data.nb_features;
      this.shadowRoot.querySelector('#project-comments .number').textContent = data.nb_comments;
    }
  }
  
  // Register the Web Component
  customElements.define('project-preview', ProjectPreview);