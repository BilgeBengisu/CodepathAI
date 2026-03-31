classDiagram
    class Customer {
        +String name
        +List~Order~ purchaseHistory
        +verifyUser() bool
        +addToHistory(order: Order)
    }

    class MenuItem {
        +String name
        +float price
        +String category
        +float popularityRating
    }

    class Menu {
        +List~MenuItem~ items
        +addItem(item: MenuItem)
        +filterByCategory(category: String) List~MenuItem~
    }

    class Order {
        +List~MenuItem~ selectedItems
        +computeTotal() float
    }

    Customer "1" --> "0..*" Order : places
    Order "1" o-- "1..*" MenuItem : contains
    Menu "1" o-- "0..*" MenuItem : manages
