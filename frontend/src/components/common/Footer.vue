<template>
  <footer class="footer">
    <div class="footer-container">
      <div class="footer-content">
        <div class="footer-section">
          <h4>地域美食推荐平台</h4>
          <p>发现各地美食，品味人间烟火</p>
        </div>
        <div class="footer-section">
          <h4>快速链接</h4>
          <ul>
            <li><router-link to="/">首页</router-link></li>
            <li><router-link to="/foods">美食</router-link></li>
            <li><router-link to="/announcements">公告</router-link></li>
          </ul>
        </div>
        <div class="footer-section">
          <h4>联系我们</h4>
          <p>邮箱: contact@foodrecommend.com</p>
          <p>电话: 400-123-4567</p>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2026 地域美食推荐平台. All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>

<style lang="scss" scoped>
.footer {
  background: var(--text-primary);
  color: #fff;
  margin-top: 60px;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px 20px;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 40px;
  margin-bottom: 30px;
}

.footer-section {
  h4 {
    color: var(--primary-color);
    margin-bottom: 15px;
    font-size: 16px;
  }
  
  p {
    color: #ccc;
    line-height: 1.6;
    margin-bottom: 8px;
  }
  
  ul {
    list-style: none;
    
    li {
      margin-bottom: 8px;
      
      a {
        color: #ccc;
        text-decoration: none;
        transition: color 0.3s;
        
        &:hover {
          color: var(--primary-color);
        }
      }
    }
  }
}

.footer-bottom {
  border-top: 1px solid #444;
  padding-top: 20px;
  text-align: center;
  
  p {
    color: #999;
    font-size: 14px;
  }
}

@media (max-width: 768px) {
  .footer-container {
    padding: 30px 15px 15px;
  }
  
  .footer-content {
    gap: 30px;
  }
}
</style>