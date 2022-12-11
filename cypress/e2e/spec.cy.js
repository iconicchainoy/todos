/// <reference types="cypress" />

describe('HomeWork Todos App', () => {
  beforeEach(() => {
      cy.visit('/')
  })

  it('Displays 4 categories by default', () => {
    cy.get('.ui.selection.dropdown').click()
    cy.get('.menu.transition div').should('have.length', 4)
    cy.get('.menu.transition div').first().should('have.text', 'School')
  })

  it('Can select class', () => {
      cy.get('.ui.selection.dropdown').click()
      cy.get('.menu.transition div').first().click()
      cy.get('.ui.divided.padded.grid div').last().should('have.text', 'School')
  })

  // TODO: Yes, this works, but it's currently abusing the test db a bit..
  // Better solution is needed
  // it('Can add category', () => {
  //     const categoryName = "Test Category"
  //     cy.get('.ui.input input').type(categoryName)
  //     cy.get('.ui.icon.button').click()
  //     cy.get('.menu.transition div').should('have.length', 6)
  //     cy.get('.menu.transition div').last().should('have.text', categoryName)

  //     // One way to delete category from API
  //     cy.request('GET', 'http://localhost:8000/api/categories').then(
  //         (response) => {
  //             expect(response.status).to.eq(200)
  //             const data = response.body
  //             const lastId = data[data.length-1].id

  //             cy.request('DELETE', 'http://localhost:8000/api/categories/delete/' + lastId).then(
  //                 (response) => {
  //                     expect(response.status).to.eq(204)
  //                 }
  //             )
  //         }
  //     )
  // })

  // it('Can delete category', () => {
  //     cy.get('.ui.selection.dropdown').click()
  //     cy.get('.menu.transition div').should('have.length', 6)
  //     cy.get('.menu.transition div').last().click()
  //     cy.get('.trash.alternate.icon').click()
  //     cy.get('.ui.selection.dropdown').click()
  //     cy.get('.menu.transition div').should('have.length', 5)
  // })

  // TODO: Same thing like at categories
  it('Can add task', () => {
      cy.get('.ui.selection.dropdown').click()
      cy.get('.menu.transition div').first().click()
      cy.get('input[name="title"]').type("Test title")
      cy.get('input[name="description"]').type("Test description")
      //cy.get('input[placeholder="YYYY-M-D"]')
      //cy.get('.ui.button').click()
  })

  // TODOs in general
  //it('Can edit task', () => {})
  //it('Can delete task', () => {})
})
